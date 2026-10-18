import { classifyEmail } from "./classifier.js";

type KnowledgeResponse = {
  answer: string;
  sources: Array<{ article_url: string; title: string; image_urls: string[] }>;
  confidence: number;
};

export async function draftReply(email: { subject?: string; body: string }) {
  const classification = classifyEmail(`${email.subject ?? ""}\n${email.body}`);
  let knowledge: KnowledgeResponse = {
    answer: "",
    sources: [],
    confidence: 0,
  };
  if (classification.intent === "how_to") {
    const response = await fetch(`${process.env.KNOWLEDGE_API_URL ?? "http://localhost:8001"}/api/v1/query`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: email.body }),
      signal: AbortSignal.timeout(15_000),
    });
    if (!response.ok) throw new Error(`Knowledge API returned HTTP ${response.status}`);
    knowledge = (await response.json()) as KnowledgeResponse;
  }
  const greeting = "Hello,";
  const context = knowledge.answer
    ? `\n\n${knowledge.answer}\n\nYou can find the relevant guide here: ${knowledge.sources[0]?.article_url ?? ""}`
    : "";
  const nextStep = classification.intent === "refund"
    ? "\n\nOur support team will review the account and applicable refund terms before confirming next steps."
    : classification.intent === "quote"
      ? "\n\nPlease share your requirements and target timeline so our team can review the scope and prepare an estimate."
      : classification.intent === "complaint"
        ? "\n\nI'm sorry this has been frustrating. Our team will investigate and follow up with you."
        : "";
  const reply = `${greeting}\n\nThank you for reaching out.${context}${nextStep}\n\nBest,\nCustomer Support`;
  return {
    reply,
    classification,
    confidence: knowledge.confidence,
    sources: knowledge.sources,
  };
}

