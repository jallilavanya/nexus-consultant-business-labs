import { z } from "zod";

export const EmailClassificationSchema = z.object({
  intent: z.enum(["how_to", "refund", "quote", "complaint", "follow_up", "other"]),
  urgency: z.enum(["low", "medium", "high"]),
  sentiment: z.enum(["positive", "neutral", "negative"]),
  requires_custom_dev: z.boolean(),
});

export type EmailClassification = z.infer<typeof EmailClassificationSchema>;

function normalizeText(text: string): string {
  return text
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\w\s']/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function classifyEmail(text: string): EmailClassification {
  const value = normalizeText(text);
  const refundIntent =
    /\b(refund|chargeback|payment reversal|reverse payment)\b/.test(value) ||
    /\b(incorrect|duplicate|unrecognized|unauthorized|unexpected|wrong)\s+(?:payment|billing|bill|charge)\b/.test(value) ||
    /\b(billed|billing|overcharged|charged twice)\b/.test(value) ||
    /\bcancel\b.*\bpayment\b/.test(value);
  const developmentIntent =
    /\b(custom|bespoke|integrat(?:e|ed|ing|ion)|develop(?:ment)?|build|implement|workflow|feature|booking|migrat(?:e|ion)|mobile app|reporting dashboard)\b/.test(value);
  const followUpIntent =
    /\bfollow(?:ing)?\s*up\b|\bfollowup\b|\bchecking in\b|\bany update\b/.test(value);
  const asksForPricing =
    /\b(can you|could you|please|we need|i need|we want|provide|send)\b.{0,60}\b(quote|quotation|estimate|pricing)\b/.test(value) ||
    /\b(quote|quotation|estimate|pricing)\b.{0,60}\b(custom|integration|project|feature|workflow|booking|migration|mobile app|crm)\b/.test(value);
  const quoteIntent = (
    /\b(quote|quotation|estimate|pricing)\b/.test(value) ||
    (developmentIntent && /\b(need|want|would like|could you|can you|please|build|create)\b/.test(value))
  ) && (!followUpIntent || asksForPricing);
  const complaintIntent =
    /\b(complaint|unacceptable|broken|not working|frustrat\w*|angry|terrible|outage|down|blocked)\b/.test(value);
  const intent = refundIntent
    ? "refund"
    : quoteIntent
      ? "quote"
      : complaintIntent
        ? "complaint"
        : followUpIntent
          ? "follow_up"
          : /\bhow do i\b|\bhow can i\b|\bwhere do i\b|\bhelp me\b|\bsteps to\b/.test(value)
            ? "how_to"
            : "other";
  return EmailClassificationSchema.parse({
    intent,
    urgency: /\burgent\b|\basap\b|\btoday\b|\bimmediately\b|\bblocked\b/.test(value)
      ? "high"
      : /\bsoon\b|\bthis week\b/.test(value)
        ? "medium"
        : "low",
    sentiment: /\bangry\b|\bfrustrat\w*\b|\bunacceptable\b|\bterrible\b|\bbroken\b|\boutage\b|\bdown\b/.test(value)
      ? "negative"
      : /\bthank\w*\b|\bgreat\b|\bappreciate\b|\blove\b/.test(value)
        ? "positive"
        : "neutral",
    requires_custom_dev:
      /\bcustom\s+(development|feature|workflow|booking|integration)\b|\bbespoke\b|\bbuild\b.*\bfeature\b/.test(value),
  });
}
