import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const name = 'dsh-step-brep-repair'
export const SKILL_NAME = 'step-brep-repair'
export const DESCRIPTION = '修补 STEP/STP CAD 模型的破面、开放曲面和实体化问题，优先保留 B-rep 曲面，检查并按需接入现有 CAD。'
const packageRoot = dirname(fileURLToPath(import.meta.url))
export const skillRoot = join(packageRoot, 'skills', SKILL_NAME)

export function apply(ctx) {
  ctx.inject(['skills'], scope => {
    const content = readFileSync(join(skillRoot, 'SKILL.md'), 'utf8')
      .replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/u, '')
    scope.skills.register({
      name: SKILL_NAME,
      description: DESCRIPTION,
      content,
      source: 'bundled',
      invocation: { modelInvocable: true, userInvocable: true },
      resourceBase: { kind: 'directory', path: skillRoot },
      provider: name,
    })
  })
}
