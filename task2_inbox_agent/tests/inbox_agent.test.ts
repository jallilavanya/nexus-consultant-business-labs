import { describe, expect, it } from "vitest";
import { classifyEmail } from "../src/agents/classifier.js";
import { LearningEngine } from "../src/agents/learningEngine.js";

type LabeledExample = readonly [message: string, expectedIntent: string];

const examples = [
  ["How do I change my password?", "how_to"],
  ["Where do I edit business hours?", "how_to"],
  ["Help me upload our company logo", "how_to"],
  ["How can I create a discount?", "how_to"],
  ["Steps to add a directory listing", "how_to"],
  ["Please refund my duplicate charge", "refund"],
  ["I want to cancel and receive a refund", "refund"],
  ["There is an incorrect charge on my bill", "refund"],
  ["Please review my payment reversal", "refund"],
  ["I was billed during my free trial", "refund"],
  ["Can you quote custom development?", "quote"],
  ["Build a custom feature for our site", "quote"],
  ["Estimate an integration with our CRM", "quote"],
  ["We need a custom booking workflow", "quote"],
  ["Quote the cost of a mobile app", "quote"],
  ["The contact form is broken", "complaint"],
  ["This is unacceptable and frustrating", "complaint"],
  ["Our member search is not working", "complaint"],
  ["The site is down and customers are blocked", "complaint"],
  ["Very angry about this terrible outage", "complaint"],
  ["Following up, any update on my ticket?", "follow_up"],
  ["Checking in about the estimate", "follow_up"],
  ["Any update on the account change?", "follow_up"],
  ["I am following up on my request", "follow_up"],
  ["Thanks, everything is great", "other"],
] as const;

function evaluateExamples(cases: readonly LabeledExample[]) {
  const started = performance.now();
  let correct = 0;
  for (const [message, expectedIntent] of cases) {
    if (classifyEmail(message).intent === expectedIntent) correct += 1;
  }
  return {
    caseCount: cases.length,
    correct,
    latencyMs: performance.now() - started,
  };
}

describe("Inbox evaluation (25 labeled examples)", () => {
  it.each(examples)("classifies %s", (message, expected) => {
    expect(classifyEmail(message).intent).toBe(expected);
  });
});

describe("classifier regression coverage", () => {
  it.each([
    ["There is an incorrect charge on my bill", "refund"],
    ["Please review my payment reversal", "refund"],
    ["I was billed during my free trial", "refund"],
    ["Estimate an integration with our CRM", "quote"],
    ["We need a custom booking workflow", "quote"],
    ["The site is down and customers are blocked", "complaint"],
    ["Very angry about this terrible outage", "complaint"],
  ] as const)("classifies the normalized support phrase: %s", (message, expected) => {
    expect(classifyEmail(`  ${message.toUpperCase()}!!!  `).intent).toBe(expected);
  });

  it("keeps billing intent ahead of negative sentiment", () => {
    expect(classifyEmail("I'm angry about an incorrect charge").intent).toBe("refund");
  });

  it("keeps quote intent ahead of a follow-up phrase", () => {
    expect(classifyEmail("Following up: please estimate our custom integration").intent).toBe("quote");
  });

  it("preserves high urgency for blocked customers", () => {
    const result = classifyEmail("The site is down and customers are blocked");
    expect(result.intent).toBe("complaint");
    expect(result.urgency).toBe("high");
    expect(result.sentiment).toBe("negative");
  });

  it("recognizes custom booking workflows as custom development", () => {
    expect(classifyEmail("We need a custom booking workflow").requires_custom_dev).toBe(true);
  });
});

describe("learning engine safety thresholds", () => {
  it("enables auto-send after exactly 20 unchanged approvals", () => {
    const engine = new LearningEngine();
    for (let index = 0; index < 19; index += 1) {
      expect(engine.record("how_to", "approved_unchanged").auto_send_enabled).toBe(false);
    }
    expect(engine.record("how_to", "approved_unchanged").auto_send_enabled).toBe(true);
  });

  it("resets the consecutive streak and revokes auto-send after a correction", () => {
    const engine = new LearningEngine();
    for (let index = 0; index < 20; index += 1) engine.record("refund", "approved_unchanged");
    const status = engine.record("refund", "edited_and_sent", true);
    expect(status.auto_send_enabled).toBe(false);
    expect(status.consecutive_approvals).toBe(0);
    expect(status.penalty_count).toBe(1);
  });

  it("prints local quality, latency, and API cost metrics", () => {
    const result = evaluateExamples(examples);
    const quality = (result.correct / result.caseCount) * 100;
    console.log(`\n| Task | Cases | Correct | Quality | Latency (ms) | Estimated API cost |\n|---|---:|---:|---:|---:|---:|\n| Inbox Agent | ${result.caseCount} | ${result.correct} | ${quality.toFixed(0)}% | ${result.latencyMs.toFixed(2)} | $0.00 (local rules) |`);
    expect(result.caseCount).toBe(25);
    expect(result.correct).toBe(result.caseCount);
  });
});
