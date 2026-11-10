import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'
import { apply, name, skillRoot, SKILL_NAME } from '../index.js'

test('bundle metadata and skill resources are coherent', () => {
  const manifest = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'))
  assert.equal(manifest.name, name)
  assert.ok(manifest.dsh.bundle.patch)
  assert.ok(readFileSync(new URL('../cordis.patch.yml', import.meta.url), 'utf8').includes(`name: ${name}`))
  for (const relative of ['SKILL.md', 'scripts/detect_cad.py', 'scripts/step_diagnose.py', 'references/cad-mcp.md']) {
    assert.ok(existsSync(join(skillRoot, relative)), relative)
  }
})

test('plugin registers a user-invocable bundled skill and its resource directory', () => {
  let captured
  apply({ inject(deps, callback) {
    assert.deepEqual(deps, ['skills'])
    callback({ skills: { register(value) { captured = value } } })
  } })
  assert.equal(captured.name, SKILL_NAME)
  assert.equal(captured.provider, name)
  assert.equal(captured.invocation.userInvocable, true)
  assert.equal(captured.invocation.modelInvocable, true)
  assert.equal(captured.resourceBase.path, skillRoot)
  assert.match(captured.content, /STEP 曲面与实体修补/u)
  assert.doesNotMatch(captured.content, /^---/u)
})
