export type OperatorAction = "approved_unchanged" | "edited_and_sent" | "overridden";

export class LearningEngine {
  private readonly consecutiveApprovals = new Map<string, number>();
  private readonly enabled = new Set<string>();
  private readonly penalties = new Map<string, number>();
  private readonly failures = new Set<string>();

  record(category: string, action: OperatorAction, wasAutoSent = false, failed = false) {
    if (action === "approved_unchanged") {
      const count = (this.consecutiveApprovals.get(category) ?? 0) + 1;
      this.consecutiveApprovals.set(category, count);
      if (count >= 20) this.enabled.add(category);
    } else {
      this.consecutiveApprovals.set(category, 0);
      if (wasAutoSent || failed || this.enabled.has(category)) this.enabled.delete(category);
      this.penalties.set(category, (this.penalties.get(category) ?? 0) + 1);
      if (failed) this.failures.add(category);
    }
    return this.status(category);
  }

  status(category: string) {
    return {
      category,
      auto_send_enabled: this.enabled.has(category),
      consecutive_approvals: this.consecutiveApprovals.get(category) ?? 0,
      penalty_count: this.penalties.get(category) ?? 0,
      failure_count: this.failures.has(category) ? 1 : 0,
    };
  }
}

export const learningEngine = new LearningEngine();
