
"use client";

import { useEffect, useState } from "react";

type Tab = "Knowledge Brain" | "Inbox Agent" | "Scope Engine";
type Email = { id: number; category: string; subject: string; body: string };

const tabs: Tab[] = ["Knowledge Brain", "Inbox Agent", "Scope Engine"];

const base = {
  knowledge:
    process.env.NEXT_PUBLIC_KNOWLEDGE_API_URL ??
    "http://localhost:8001",
  inbox:
    process.env.NEXT_PUBLIC_INBOX_API_URL ??
    "http://localhost:8002/api/v1",
  scope:
    process.env.NEXT_PUBLIC_SCOPE_API_URL ??
    "http://localhost:8003",
};

export default function Home() {
  const [tab, setTab] = useState<Tab>("Knowledge Brain");
  const [notice, setNotice] = useState("");

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brand-mark">N</span>
          <span>
            NEXUS <b>CONSULTANT</b>
          </span>
        </a>

        <div className="top-meta">
          <span className="live-dot" /> All systems operational{" "}
          <span className="avatar">LC</span>
        </div>
      </header>

      <section className="welcome">
        <div>
          <div className="eyebrow">AI OPERATIONS SUITE</div>
          <h1>
            Your expertise, <em>in sync.</em>
          </h1>
          <p>
            One clear view across customer knowledge, support, and project
            delivery.
          </p>
        </div>

        <div className="date-card">
          <span>WORKSPACE</span>
          <strong>Consulting operations</strong>
          <small>3 intelligent workflows</small>
        </div>
      </section>

      <nav className="tabs" aria-label="Workspace tools">
        {tabs.map((item, index) => (
          <button
            key={item}
            className={`tab ${tab === item ? "active" : ""}`}
            onClick={() => {
              setTab(item);
              setNotice("");
            }}
          >
            <span className="tab-index">0{index + 1}</span>
            {item}
          </button>
        ))}
      </nav>

      {notice && (
        <div className="notice" role="status">
          {notice}
        </div>
      )}

      {tab === "Knowledge Brain" && <KnowledgePanel setNotice={setNotice} />}
      {tab === "Inbox Agent" && <InboxPanel setNotice={setNotice} />}
      {tab === "Scope Engine" && <ScopePanel setNotice={setNotice} />}

      <footer>
        BUILT FOR BETTER WORK{" "}
        <span>AI Tech Consultant · Preview</span>
      </footer>
    </main>
  );
}

function KnowledgePanel({
  setNotice,
}: {
  setNotice: (value: string) => void;
}) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function ask(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setNotice("");

    try {
      const response = await fetch(`${base.knowledge}/api/v1/query`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error(`Knowledge service returned ${response.status}`);
      }

      setResult(await response.json());
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Knowledge request failed."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">01 / KNOWLEDGE BRAIN</div>
          <h2>Find the right answer.</h2>
          <p>
            Ask a question and get grounded guidance from your help center.
          </p>
        </div>
        <span className="pill">● &nbsp;Connected to help center</span>
      </div>

      <form className="ask-box" onSubmit={ask}>
        <label htmlFor="question">What would you like to know?</label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="e.g. How do I update a member’s profile?"
          required
          minLength={2}
        />
        <button className="primary" disabled={busy}>
          {busy ? "Searching…" : "Ask the knowledge brain"} <span>↗</span>
        </button>
      </form>

      {result && (
        <div className="answer">
          <div className="answer-top">
            <span className="eyebrow">ANSWER</span>
            <span className="confidence">
              Confidence {Math.round(result.confidence * 100)}%
            </span>
          </div>

          <p>{result.answer}</p>

          {!!result.sources?.length && (
            <div className="sources">
              <h3>Sources &amp; visual evidence</h3>
              <div className="source-grid">
                {result.sources.map((source: any, index: number) => (
                  <article
                    className="source-card"
                    key={`${source.article_url}-${index}`}
                  >
                    <div className="source-number">
                      SOURCE 0{index + 1}
                    </div>
                    <a
                      href={source.article_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {source.title} ↗
                    </a>
                    <p>{source.excerpt}</p>

                    {source.image_urls?.map((url: string) => (
                      <img
                        key={url}
                        src={url}
                        alt={`Help center screenshot from ${source.title}`}
                      />
                    ))}
                  </article>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}

function InboxPanel({
  setNotice,
}: {
  setNotice: (value: string) => void;
}) {
  const [emailList, setEmailList] = useState<Email[]>([]);
  const [selected, setSelected] = useState<Email | null>(null);
  const [draft, setDraft] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [classification, setClassification] = useState<any>(null);
  const [auto, setAuto] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(`${base.inbox}/emails`)
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`Inbox service returned ${response.status}`);
        }

        const data = (await response.json()) as Email[];
        setEmailList(data);

        if (data.length) {
          setSelected(data[0]);
        }
      })
      .catch((error) =>
        setNotice(
          error instanceof Error
            ? error.message
            : "Could not load sample emails."
        )
      );
  }, [setNotice]);

  async function createDraft(email: Email) {
    setSelected(email);
    setBusy(true);
    setNotice("");

    try {
      const response = await fetch(`${base.inbox}/draft`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          subject: email.subject,
          body: email.body,
        }),
      });

      if (!response.ok) {
        throw new Error(`Inbox service returned ${response.status}`);
      }

      const data = await response.json();

      setDraft(data.reply);
      setConfidence(data.confidence);
      setClassification(data.classification);

      const status = await fetch(
        `${base.inbox}/auto-send/${encodeURIComponent(
          data.classification.intent
        )}`
      );

      setAuto(status.ok ? await status.json() : null);
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Could not create a draft."
      );
    } finally {
      setBusy(false);
    }
  }

  async function feedback(action: string) {
    try {
      const response = await fetch(`${base.inbox}/feedback`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          // FIX: selected can be null, so use optional chaining.
          category:
            classification?.intent ?? selected?.category ?? "",
          action,
        }),
      });

      if (!response.ok) {
        throw new Error(`Feedback failed (${response.status})`);
      }

      setAuto(await response.json());

      setNotice(
        action === "approved_unchanged"
          ? "Draft approved and recorded for learning."
          : "Draft feedback recorded."
      );
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Feedback could not be saved."
      );
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">02 / INBOX AGENT</div>
          <h2>Support that stays personal.</h2>
          <p>
            Review customer messages, AI-assisted replies, and team
            automation.
          </p>
        </div>
        <span className="pill">50 sample emails</span>
      </div>

      <div className="inbox-layout">
        <aside className="email-list">
          <div className="list-title">
            INCOMING <span>{emailList.length}</span>
          </div>

          {emailList.map((email) => (
            <button
              className={`email-row ${
                selected?.id === email.id ? "chosen" : ""
              }`}
              key={email.id}
              onClick={() => createDraft(email)}
            >
              <span className="email-avatar">{email.subject[0]}</span>

              <span className="email-info">
                <b>{email.subject}</b>
                <small>{email.body}</small>
                <em>{email.category.replace("_", " ")}</em>
              </span>
            </button>
          ))}
        </aside>

        <div className="draft-area">
          <div className="draft-heading">
            <div>
              <span className="eyebrow">CUSTOMER MESSAGE</span>
              <h3>{selected?.subject ?? "Choose an email"}</h3>
            </div>
            <span className="confidence">
              AI confidence {Math.round(confidence * 100)}%
            </span>
          </div>

          <blockquote>
            {selected?.body ??
              "Select a customer email to create a response draft."}
          </blockquote>

          <div className="draft-heading">
            <div>
              <span className="eyebrow">SUGGESTED REPLY</span>
              <h3>Draft response</h3>
            </div>

            {classification && (
              <span className="tag">
                {classification.intent.replace("_", " ")}
              </span>
            )}
          </div>

          <textarea
            className="draft-editor"
            value={draft}
            disabled={busy}
            onChange={(event) => setDraft(event.target.value)}
            aria-label="Draft response"
            placeholder="Select an email to generate a draft."
          />

          <div className="approval-bar">
            <div className="auto-state">
              <span
                className={
                  auto?.auto_send_enabled ? "live-dot" : "grey-dot"
                }
              />
              Auto-send{" "}
              {auto?.auto_send_enabled
                ? "enabled"
                : "review required"}{" "}
              · demo feedback only
            </div>

            <div className="action-buttons">
              <button
                className="secondary"
                disabled={!selected}
                onClick={() => feedback("overridden")}
              >
                Manual reply
              </button>

              <button
                className="secondary"
                disabled={!selected}
                onClick={() => feedback("edited_and_sent")}
              >
                Edit &amp; send
              </button>

              <button
                className="primary"
                disabled={!selected}
                onClick={() => feedback("approved_unchanged")}
              >
                Approve draft ↗
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ScopePanel({
  setNotice,
}: {
  setNotice: (value: string) => void;
}) {
  const [transcript, setTranscript] = useState("");
  const [client, setClient] = useState("Acme Directory");
  const [scope, setScope] = useState<any>(null);
  const [followup, setFollowup] = useState("");
  const [delta, setDelta] = useState<any>(null);
  const [busy, setBusy] = useState(false);

  async function generate(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setNotice("");

    try {
      const response = await fetch(`${base.scope}/api/v1/scope`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          transcript,
          client_name: client,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Scope service returned ${response.status}: ${await response.text()}`
        );
      }

      setScope(await response.json());
      setDelta(null);
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Scope generation failed."
      );
    } finally {
      setBusy(false);
    }
  }

  async function compare(event: React.FormEvent) {
    event.preventDefault();

    if (!scope) return;

    setBusy(true);

    try {
      const response = await fetch(`${base.scope}/api/v1/scope/delta`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          baseline: scope.tasks,
          follow_up_transcript: followup,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Scope comparison failed (${response.status}): ${await response.text()}`
        );
      }

      setDelta(await response.json());
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Scope comparison failed."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <div className="eyebrow">03 / SCOPE ENGINE</div>
          <h2>Turn conversations into clarity.</h2>
          <p>
            Translate meeting notes into a transparent, reviewable project
            scope.
          </p>
        </div>
        <span className="pill">Effort &amp; pricing estimate</span>
      </div>

      <form className="scope-input" onSubmit={generate}>
        <label>
          Client name
          <input
            value={client}
            onChange={(event) => setClient(event.target.value)}
          />
        </label>

        <label>
          Meeting transcript
          <textarea
            value={transcript}
            onChange={(event) => setTranscript(event.target.value)}
            placeholder="Paste meeting notes or a transcript…"
            required
            minLength={10}
          />
        </label>

        <button className="primary" disabled={busy}>
          {busy
            ? "Analyzing…"
            : "Generate statement of work ↗"}
        </button>
      </form>

      {scope && (
        <div className="scope-results">
          <div className="metrics">
            <div>
              <span>ESTIMATED HOURS</span>
              <strong>{scope.total_hours}</strong>
            </div>

            <div>
              <span>ESTIMATED SERVICES</span>
              <strong>
                ${Number(scope.total_cost).toLocaleString()}
              </strong>
            </div>

            <div>
              <span>DELIVERABLES</span>
              <strong>{scope.tasks.length}</strong>
            </div>
          </div>

          <h3>Itemized work plan</h3>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Task</th>
                  <th>Product fit</th>
                  <th>Complexity</th>
                  <th>Hours</th>
                  <th>Estimate</th>
                </tr>
              </thead>

              <tbody>
                {scope.tasks.map((task: any, index: number) => (
                  <tr key={`${task.title}-${index}`}>
                    <td>{task.title}</td>
                    <td>{task.product_fit}</td>
                    <td>{task.complexity}</td>
                    <td>{task.estimated_hours}</td>
                    <td>${Number(task.cost).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <details>
            <summary>Client proposal preview</summary>
            <pre>{scope.proposal_markdown}</pre>
          </details>

          <form className="delta-form" onSubmit={compare}>
            <label>
              Meeting 2 — compare scope changes
              <textarea
                value={followup}
                onChange={(event) => setFollowup(event.target.value)}
                placeholder="Paste follow-up meeting notes…"
                required
                minLength={10}
              />
            </label>

            <button className="secondary" disabled={busy}>
              Compare against baseline
            </button>
          </form>

          {delta && (
            <div className="delta-grid">
              {[
                ["New Tasks", delta.new_tasks],
                [
                  "Modified Tasks",
                  delta.modified_tasks.map((item: any) => item.after),
                ],
                ["Removed Tasks", delta.removed_tasks],
                ["Out-of-Scope · Extra Cost", delta.out_of_scope_items],
              ].map(([title, items]: any) => (
                <article className="delta-card" key={title}>
                  <h4>{title}</h4>

                  {items.length ? (
                    items.map((item: any, index: number) => (
                      <p key={index}>{item.title}</p>
                    ))
                  ) : (
                    <p className="muted">No changes</p>
                  )}
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}