// The public ledger (ledger/ledger.jsonl), bundled at build time. Only what the ledger itself
// says is shown: which forecast dates are sealed, when, and their hashes. No forecast, no score.
import entries from "virtual:ledger";
import { meta } from "./data";

export interface Entry {
  seq: number;
  kind: string;
  origin: string | null;
  payload_sha256: string;
  prev: string;
  recorded_utc: string;
  entry_hash: string;
}
export const REPO_URL = "https://github.com/vrraiv/foundation-forecast";
export const ledger = entries as Entry[];
export const preregistration = ledger.find((e) => e.kind === "preregistration");
export const runs = ledger.filter((e) => e.kind === "run" && e.origin);
export const sealed = new Set(runs.map((e) => e.origin)).size;
export const needed = meta.live_first_scoring_min_origins;
/** "1 of 12 sealed" until the threshold is passed, then just the count. */
export const sealedLabel = sealed <= needed ? `${sealed} of ${needed} sealed` : `${sealed} forecast dates sealed`;
export const releaseUrl = (origin: string) => `${REPO_URL}/releases/tag/registry-${origin}`;
