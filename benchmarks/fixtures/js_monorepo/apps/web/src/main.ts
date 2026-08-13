import { normalizeName } from "../../../packages/shared/src/index";

export function greeting(name: string): string {
  return `Hello ${normalizeName(name)}`;
}
