from __future__ import annotations

import unittest

from dreampipe.adapters.glm_adapter import GLMAdapter, GLMConfig, GLMPromptCompiler


class FakeGLM(GLMAdapter):
    def __init__(self, content: dict):
        super().__init__(GLMConfig(api_key="test-key"))
        self.content = content

    def chat_json(self, messages, *, temperature=0.2):
        return self.content


class GLMAdapterTests(unittest.TestCase):
    def test_prompt_compiler_returns_provider_contract(self):
        compiler = GLMPromptCompiler(FakeGLM({"prompt": "vertical cinematic shot", "negative_prompt": "no watermark"}))
        result = compiler.compile(
            shot={"shot_id": "S01"},
            project_bible={"project_id": "demo"},
            brief={"cta": "go"},
            target_model="happyhorse-1.1-i2v",
        )
        self.assertEqual(result, {"prompt": "vertical cinematic shot", "negative_prompt": "no watermark"})

    def test_missing_key_is_rejected_before_network_call(self):
        adapter = GLMAdapter(GLMConfig())
        with self.assertRaisesRegex(Exception, "GLM_API_KEY"):
            adapter.chat_json([{"role": "user", "content": "test"}])


if __name__ == "__main__":
    unittest.main()
