import { Router } from "express";
import { draftReply } from "../agents/drafter.js";
import { learningEngine, type OperatorAction } from "../agents/learningEngine.js";
import { z } from "zod";
import sampleEmails from "../data/sample_emails.json";
export const router = Router();
const FeedbackSchema = z.object({
  category: z.string().min(1),
  action: z.enum(["approved_unchanged", "edited_and_sent", "overridden"]),
  was_auto_sent: z.boolean().default(false),
  failed: z.boolean().default(false),
});

router.get("/health", (_request, response) => response.json({ status: "ok" }));
router.get("/emails", (_request, response) => response.json(sampleEmails));

router.post("/draft", async (request, response, next) => {
  try {
    const input = z.object({ subject: z.string().optional(), body: z.string().min(2) }).parse(request.body);
    response.json(await draftReply(input));
  } catch (error) {
    next(error);
  }
});

router.post("/feedback", (request, response, next) => {
  try {
    const input = FeedbackSchema.parse(request.body);
    response.json(learningEngine.record(input.category, input.action as OperatorAction, input.was_auto_sent, input.failed));
  } catch (error) {
    next(error);
  }
});

router.get("/auto-send/:category", (request, response) => {
  response.json(learningEngine.status(request.params.category));
});
