import cors from "cors";
import express, { type ErrorRequestHandler } from "express";
import { ZodError } from "zod";
import { router } from "./api/routes.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "1mb" }));
app.use("/api/v1", router);
const errors: ErrorRequestHandler = (error, _request, response, _next) => {
  if (error instanceof ZodError) {
    response.status(400).json({ error: "Invalid request", details: error.issues });
    return;
  }
  console.error("Inbox agent request failed", error);
  response.status(500).json({ error: "Inbox request failed" });
};
app.use(errors);

const port = Number(process.env.PORT ?? 8002);
app.listen(port, "0.0.0.0", () => console.log(`Inbox Agent listening on ${port}`));

