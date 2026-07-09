POPULAR_PROVIDERS = [
    ("Anthropic (Official)", "anthropic", "https://api.anthropic.com", "claude-3-5-sonnet-20241022", "Official Anthropic API"),
    ("Anthropic — Claude 3.5 Sonnet", "anthropic", "https://api.anthropic.com", "claude-3-5-sonnet-20241022", "Latest Sonnet model"),
    ("Anthropic — Claude 3.5 Haiku", "anthropic", "https://api.anthropic.com", "claude-3-5-haiku-20241022", "Fast, efficient model"),
    ("Anthropic — Claude 3 Opus", "anthropic", "https://api.anthropic.com", "claude-3-opus-20240229", "Most capable model"),
    ("Anthropic — Claude 3 Sonnet", "anthropic", "https://api.anthropic.com", "claude-3-sonnet-20240229", "Balanced capability/speed"),
    ("Anthropic — Claude 3 Haiku", "anthropic", "https://api.anthropic.com", "claude-3-haiku-20240307", "Fast, lightweight"),

    ("OpenAI (Official)", "openai", "https://api.openai.com/v1", "gpt-4o", "Official OpenAI API"),
    ("OpenAI — GPT-4o", "openai", "https://api.openai.com/v1", "gpt-4o", "Multimodal flagship"),
    ("OpenAI — GPT-4o Mini", "openai", "https://api.openai.com/v1", "gpt-4o-mini", "Fast, cheap GPT-4o"),
    ("OpenAI — GPT-4 Turbo", "openai", "https://api.openai.com/v1", "gpt-4-turbo", "Previous flagship"),
    ("OpenAI — GPT-4", "openai", "https://api.openai.com/v1", "gpt-4", "Original GPT-4"),
    ("OpenAI — GPT-3.5 Turbo", "openai", "https://api.openai.com/v1", "gpt-3.5-turbo", "Fast, cost-effective"),
    ("OpenAI — o1 Preview", "openai", "https://api.openai.com/v1", "o1-preview", "Reasoning model"),
    ("OpenAI — o1 Mini", "openai", "https://api.openai.com/v1", "o1-mini", "Smaller reasoning model"),

    ("Azure OpenAI", "openai-compatible", "https://<resource>.openai.azure.com", "gpt-4o", "Microsoft Azure OpenAI Service"),
    ("Google Vertex AI (Gemini)", "openai-compatible", "https://<region>-aiplatform.googleapis.com/v1beta1/projects/<project>/locations/<region>/endpoints/openapi", "gemini-1.5-pro", "Google Cloud Vertex AI"),
    ("AWS Bedrock (Anthropic)", "openai-compatible", "https://bedrock-runtime.<region>.amazonaws.com", "anthropic.claude-3-5-sonnet-20240620-v1:0", "AWS Bedrock with Anthropic models"),
    ("AWS Bedrock (Meta Llama)", "openai-compatible", "https://bedrock-runtime.<region>.amazonaws.com", "meta.llama3-1-70b-instruct-v1:0", "AWS Bedrock with Llama models"),
    ("AWS Bedrock (Cohere)", "openai-compatible", "https://bedrock-runtime.<region>.amazonaws.com", "cohere.command-r-plus-v1:0", "AWS Bedrock with Cohere models"),
    ("AWS Bedrock (Mistral)", "openai-compatible", "https://bedrock-runtime.<region>.amazonaws.com", "mistral.mistral-large-2407-v1:0", "AWS Bedrock with Mistral models"),

    ("Together AI", "openai-compatible", "https://api.together.xyz/v1", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "Together AI inference"),
    ("Together AI — Llama 3.1 405B", "openai-compatible", "https://api.together.xyz/v1", "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", "Largest open Llama"),
    ("Together AI — Llama 3.1 70B", "openai-compatible", "https://api.together.xyz/v1", "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", "Popular 70B model"),
    ("Together AI — Llama 3.1 8B", "openai-compatible", "https://api.together.xyz/v1", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", "Fast 8B model"),
    ("Together AI — Mixtral 8x22B", "openai-compatible", "https://api.together.xyz/v1", "mistralai/Mixtral-8x22B-Instruct-v0.1", "Mistral MoE model"),
    ("Together AI — Qwen 2.5 72B", "openai-compatible", "https://api.together.xyz/v1", "Qwen/Qwen2.5-72B-Instruct-Turbo", "Alibaba Qwen model"),
    ("Together AI — DeepSeek V3", "openai-compatible", "https://api.together.xyz/v1", "deepseek-ai/DeepSeek-V3", "DeepSeek large model"),

    ("Fireworks AI", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/llama-v3p1-70b-instruct", "Fireworks inference"),
    ("Fireworks — Llama 3.1 405B", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/llama-v3p1-405b-instruct", "Largest Llama"),
    ("Fireworks — Llama 3.1 70B", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/llama-v3p1-70b-instruct", "Popular 70B"),
    ("Fireworks — Mixtral 8x22B", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/mixtral-8x22b-instruct", "Mistral MoE"),
    ("Fireworks — DeepSeek V2.5", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/deepseek-v2-5", "DeepSeek model"),
    ("Fireworks — Qwen 2.5 72B", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/qwen2p5-72b-instruct", "Qwen model"),
    ("Fireworks — Phi-3.5 Mini", "openai-compatible", "https://api.fireworks.ai/inference/v1", "accounts/fireworks/models/phi-3p5-mini-instruct", "Microsoft small model"),

    ("Groq", "openai-compatible", "https://api.groq.com/openai/v1", "llama-3.1-70b-versatile", "Ultra-fast inference"),
    ("Groq — Llama 3.1 70B", "openai-compatible", "https://api.groq.com/openai/v1", "llama-3.1-70b-versatile", "Fast 70B"),
    ("Groq — Llama 3.1 8B", "openai-compatible", "https://api.groq.com/openai/v1", "llama-3.1-8b-instant", "Fast 8B"),
    ("Groq — Mixtral 8x7B", "openai-compatible", "https://api.groq.com/openai/v1", "mixtral-8x7b-32768", "Mistral MoE"),
    ("Groq — Gemma 2 9B", "openai-compatible", "https://api.groq.com/openai/v1", "gemma2-9b-it", "Google Gemma"),
    ("Groq — Qwen 2.5 32B", "openai-compatible", "https://api.groq.com/openai/v1", "qwen-2.5-32b", "Qwen model"),

    ("Cerebras", "openai-compatible", "https://api.cerebras.ai/v1", "llama3.1-70b", "Cerebras wafer-scale"),
    ("Cerebras — Llama 3.1 70B", "openai-compatible", "https://api.cerebras.ai/v1", "llama3.1-70b", "Fast 70B"),
    ("Cerebras — Llama 3.1 8B", "openai-compatible", "https://api.cerebras.ai/v1", "llama3.1-8b", "Fast 8B"),

    ("SambaNova", "openai-compatible", "https://api.sambanova.ai/v1", "Meta-Llama-3.1-70B-Instruct", "SambaNova Cloud"),
    ("SambaNova — Llama 3.1 405B", "openai-compatible", "https://api.sambanova.ai/v1", "Meta-Llama-3.1-405B-Instruct", "Largest Llama"),
    ("SambaNova — Llama 3.1 70B", "openai-compatible", "https://api.sambanova.ai/v1", "Meta-Llama-3.1-70B-Instruct", "Popular 70B"),
    ("SambaNova — Llama 3.1 8B", "openai-compatible", "https://api.sambanova.ai/v1", "Meta-Llama-3.1-8B-Instruct", "Fast 8B"),

    ("Anyscale Endpoints", "openai-compatible", "https://api.endpoints.anyscale.com/v1", "meta-llama/Meta-Llama-3.1-70B-Instruct", "Anyscale Ray-based"),
    ("Anyscale — Llama 3.1 70B", "openai-compatible", "https://api.endpoints.anyscale.com/v1", "meta-llama/Meta-Llama-3.1-70B-Instruct", "Ray-based 70B"),
    ("Anyscale — Llama 3.1 8B", "openai-compatible", "https://api.endpoints.anyscale.com/v1", "meta-llama/Meta-Llama-3.1-8B-Instruct", "Ray-based 8B"),
    ("Anyscale — Mixtral 8x22B", "openai-compatible", "https://api.endpoints.anyscale.com/v1", "mistralai/Mixtral-8x22B-Instruct-v0.1", "Ray-based Mixtral"),

    ("Perplexity AI", "openai-compatible", "https://api.perplexity.ai", "llama-3.1-sonar-large-128k-online", "Search-augmented LLMs"),
    ("Perplexity — Sonar Large", "openai-compatible", "https://api.perplexity.ai", "llama-3.1-sonar-large-128k-online", "Large search model"),
    ("Perplexity — Sonar Small", "openai-compatible", "https://api.perplexity.ai", "llama-3.1-sonar-small-128k-online", "Small search model"),
    ("Perplexity — Sonar Huge", "openai-compatible", "https://api.perplexity.ai", "llama-3.1-sonar-huge-128k-online", "Huge search model"),

    ("Mistral AI (Official)", "openai-compatible", "https://api.mistral.ai/v1", "mistral-large-latest", "Official Mistral API"),
    ("Mistral — Large 2", "openai-compatible", "https://api.mistral.ai/v1", "mistral-large-2407", "Latest large model"),
    ("Mistral — Small", "openai-compatible", "https://api.mistral.ai/v1", "mistral-small-latest", "Efficient small model"),
    ("Mistral — Nemo", "openai-compatible", "https://api.mistral.ai/v1", "open-mistral-nemo", "Open Nemo model"),
    ("Mistral — Codestral", "openai-compatible", "https://api.mistral.ai/v1", "codestral-latest", "Code-specialized"),

    ("Cohere (Official)", "openai-compatible", "https://api.cohere.ai/v1", "command-r-plus", "Official Cohere API"),
    ("Cohere — Command R+", "openai-compatible", "https://api.cohere.ai/v1", "command-r-plus", "Flagship RAG model"),
    ("Cohere — Command R", "openai-compatible", "https://api.cohere.ai/v1", "command-r", "Efficient RAG model"),
    ("Cohere — Aya 23", "openai-compatible", "https://api.cohere.ai/v1", "aya-23-35b", "Multilingual model"),

    ("DeepSeek (Official)", "openai-compatible", "https://api.deepseek.com/v1", "deepseek-chat", "Official DeepSeek API"),
    ("DeepSeek — V3", "openai-compatible", "https://api.deepseek.com/v1", "deepseek-chat", "Latest V3 model"),
    ("DeepSeek — Coder", "openai-compatible", "https://api.deepseek.com/v1", "deepseek-coder", "Code-specialized"),

    ("Z.ai / Zhipu", "openai-compatible", "https://open.bigmodel.cn/api/paas/v4", "glm-4-plus", "Chinese LLM provider"),
    ("Z.ai — GLM-4 Plus", "openai-compatible", "https://open.bigmodel.cn/api/paas/v4", "glm-4-plus", "Latest GLM model"),
    ("Z.ai — GLM-4 Flash", "openai-compatible", "https://open.bigmodel.cn/api/paas/v4", "glm-4-flash", "Fast GLM model"),

    ("Moonshot AI (Kimi)", "openai-compatible", "https://api.moonshot.cn/v1", "moonshot-v1-8k", "Chinese LLM provider"),
    ("Moonshot — Kimi 8K", "openai-compatible", "https://api.moonshot.cn/v1", "moonshot-v1-8k", "8K context"),
    ("Moonshot — Kimi 32K", "openai-compatible", "https://api.moonshot.cn/v1", "moonshot-v1-32k", "32K context"),
    ("Moonshot — Kimi 128K", "openai-compatible", "https://api.moonshot.cn/v1", "moonshot-v1-128k", "128K context"),

    ("MiniMax", "openai-compatible", "https://api.minimax.chat/v1", "abab6.5s-chat", "Chinese LLM provider"),
    ("MiniMax — abab6.5s", "openai-compatible", "https://api.minimax.chat/v1", "abab6.5s-chat", "Latest model"),

    ("Baichuan", "openai-compatible", "https://api.baichuan-ai.com/v1", "Baichuan4", "Chinese LLM provider"),
    ("Baichuan — Baichuan4", "openai-compatible", "https://api.baichuan-ai.com/v1", "Baichuan4", "Latest model"),

    ("01.AI (Yi)", "openai-compatible", "https://api.lingyiwanwu.com/v1", "yi-large", "Chinese LLM provider"),
    ("01.AI — Yi Large", "openai-compatible", "https://api.lingyiwanwu.com/v1", "yi-large", "Large model"),
    ("01.AI — Yi Medium", "openai-compatible", "https://api.lingyiwanwu.com/v1", "yi-medium", "Medium model"),

    ("StepFun", "openai-compatible", "https://api.stepfun.com/v1", "step-1-8k", "Chinese LLM provider"),
    ("StepFun — Step-1", "openai-compatible", "https://api.stepfun.com/v1", "step-1-8k", "Main model"),

    ("X.ai / Grok", "openai-compatible", "https://api.x.ai/v1", "grok-beta", "Elon Musk's xAI"),
    ("X.ai — Grok Beta", "openai-compatible", "https://api.x.ai/v1", "grok-beta", "Beta model"),

    ("NVIDIA NIM", "openai-compatible", "https://integrate.api.nvidia.com/v1", "meta/llama-3.1-70b-instruct", "NVIDIA Inference Microservices"),
    ("NVIDIA — Nemotron 3 Ultra", "openai-compatible", "https://integrate.api.nvidia.com/v1", "nvidia/nemotron-3-ultra", "NVIDIA reasoning model"),
    ("NVIDIA — Nemotron 4 340B", "openai-compatible", "https://integrate.api.nvidia.com/v1", "nvidia/nemotron-4-340b-instruct", "Large Nemotron"),

    ("Replicate", "openai-compatible", "https://api.replicate.com/v1", "meta/meta-llama-3.1-70b-instruct", "Model hosting platform"),
    ("Replicate — Llama 3.1 405B", "openai-compatible", "https://api.replicate.com/v1", "meta/meta-llama-3.1-405b-instruct", "Largest Llama"),
    ("Replicate — Llama 3.1 70B", "openai-compatible", "https://api.replicate.com/v1", "meta/meta-llama-3.1-70b-instruct", "Popular 70B"),
    ("Replicate — Mixtral 8x22B", "openai-compatible", "https://api.replicate.com/v1", "mistralai/mixtral-8x22b-instruct-v0.1", "Mistral MoE"),

    ("Hugging Face Inference", "openai-compatible", "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-70B-Instruct", "meta-llama/Meta-Llama-3.1-70B-Instruct", "HF Inference API"),
    ("HF — Llama 3.1 70B", "openai-compatible", "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-70B-Instruct", "meta-llama/Meta-Llama-3.1-70B-Instruct", "Popular 70B"),
    ("HF — Mixtral 8x7B", "openai-compatible", "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1", "mistralai/Mixtral-8x7B-Instruct-v0.1", "Mistral MoE"),
    ("HF — Qwen 2.5 72B", "openai-compatible", "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct", "Qwen/Qwen2.5-72B-Instruct", "Qwen model"),

    ("Ollama (Local)", "ollama", "http://localhost:11434", "llama3.1", "Local Ollama instance"),
    ("Ollama — Llama 3.1 70B", "ollama", "http://localhost:11434", "llama3.1:70b", "Local 70B"),
    ("Ollama — Llama 3.1 8B", "ollama", "http://localhost:11434", "llama3.1:8b", "Local 8B"),
    ("Ollama — Mistral 7B", "ollama", "http://localhost:11434", "mistral:7b", "Local Mistral"),
    ("Ollama — Mixtral 8x7B", "ollama", "http://localhost:11434", "mixtral:8x7b", "Local Mixtral"),
    ("Ollama — Qwen 2.5 72B", "ollama", "http://localhost:11434", "qwen2.5:72b", "Local Qwen"),
    ("Ollama — DeepSeek Coder", "ollama", "http://localhost:11434", "deepseek-coder:33b", "Local code model"),
    ("Ollama — Phi-3.5 Mini", "ollama", "http://localhost:11434", "phi3.5:mini", "Local small model"),
    ("Ollama — Gemma 2 9B", "ollama", "http://localhost:11434", "gemma2:9b", "Local Gemma"),
    ("Ollama — Code Llama 70B", "ollama", "http://localhost:11434", "codellama:70b", "Local code model"),

    ("LM Studio (Local)", "openai-compatible", "http://localhost:1234/v1", "local-model", "Local LM Studio server"),
    ("LM Studio — Any Model", "openai-compatible", "http://localhost:1234/v1", "", "Load any GGUF in LM Studio"),

    ("Text Gen WebUI (Local)", "openai-compatible", "http://localhost:5000/v1", "local-model", "Local Oobabooga server"),

    ("vLLM (Local)", "openai-compatible", "http://localhost:8000/v1", "local-model", "Local vLLM server"),

    ("TGI (Local)", "openai-compatible", "http://localhost:8080/v1", "local-model", "Local TGI server"),

    ("OpenRouter", "openai-compatible", "https://openrouter.ai/api/v1", "openrouter/auto", "Model aggregator/gateway"),
    ("OpenRouter — Auto", "openai-compatible", "https://openrouter.ai/api/v1", "openrouter/auto", "Auto-select best model"),
    ("OpenRouter — Claude 3.5 Sonnet", "openai-compatible", "https://openrouter.ai/api/v1", "anthropic/claude-3.5-sonnet", "Via OpenRouter"),
    ("OpenRouter — GPT-4o", "openai-compatible", "https://openrouter.ai/api/v1", "openai/gpt-4o", "Via OpenRouter"),
    ("OpenRouter — Llama 3.1 405B", "openai-compatible", "https://openrouter.ai/api/v1", "meta-llama/llama-3.1-405b-instruct", "Via OpenRouter"),
    ("OpenRouter — DeepSeek V3", "openai-compatible", "https://openrouter.ai/api/v1", "deepseek/deepseek-chat", "Via OpenRouter"),

    ("Requesty", "openai-compatible", "https://router.requesty.ai/v1", "requesty/auto", "Model router"),
    ("Requesty — Auto", "openai-compatible", "https://router.requesty.ai/v1", "requesty/auto", "Auto-select"),

    ("LiteLLM Proxy (Self-hosted)", "openai-compatible", "http://localhost:4000/v1", "any", "Self-hosted model gateway"),

    ("Portkey", "openai-compatible", "https://api.portkey.ai/v1", "portkey/auto", "AI gateway"),
    ("Portkey — Auto", "openai-compatible", "https://api.portkey.ai/v1", "portkey/auto", "Auto-route"),

    ("Helicone Proxy", "openai-compatible", "https://oai.helicone.ai/v1", "any", "Observability proxy"),

    ("Langfuse Gateway", "openai-compatible", "https://cloud.langfuse.com/gateway/v1", "any", "Observability gateway"),

    ("Custom OpenAI-Compatible", "openai-compatible", "", "", "Any OpenAI-compatible endpoint"),
    ("Custom Anthropic-Compatible", "anthropic", "", "", "Any Anthropic-compatible endpoint"),
    ("Custom Ollama", "ollama", "", "", "Custom Ollama host"),
]


def get_provider_kinds() -> list[str]:
    kinds = set()
    for _, kind, _, _, _ in POPULAR_PROVIDERS:
        kinds.add(kind)
    return sorted(kinds)


def search_providers(query: str) -> list[tuple]:
    query = query.lower().strip()
    if not query:
        return POPULAR_PROVIDERS
    results = []
    for entry in POPULAR_PROVIDERS:
        name, kind, base_url, model, desc = entry
        if query in name.lower() or query in desc.lower() or query in kind.lower():
            results.append(entry)
    return results