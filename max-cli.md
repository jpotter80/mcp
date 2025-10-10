max CLI
The max command line tool allows you to create an OpenAI-compatible endpoint with a simple max serve command. It also includes a command to benchmark your endpoint using built-in datasets or your own dataset.

Install
You can install the max CLI with the modular package.

pixi
uv
pip
conda
If you don't have it, install pixi:
curl -fsSL https://pixi.sh/install.sh | sh

Then restart your terminal for the changes to take effect.

Create a project:
pixi init example-project \
  -c https://conda.modular.com/max-nightly/ -c conda-forge \
  && cd example-project

Tip: You can skip the -c options if you add these channels as defaults.

Install the modular conda package:
Nightly
Stable
pixi add "modular==25.6"

Start the virtual environment:
pixi shell

You can print all the available commands and options with --help:

max --help

max serve --help

max benchmark
Runs comprehensive benchmark tests on an active model server to measure performance metrics including throughput, latency, and resource utilization.

max benchmark [OPTIONS]

For a full list of options, run max benchmark --help.

Before running this command, make sure the model server is running, via max serve.

The max benchmark command is a convenient packaging for our open-source benchmark_serving.py script and accepts all the same options.

Example

Benchmark the google/gemma-3-27b-it model already running on localhost:

max benchmark \
  --model google/gemma-3-27b-it \
  --backend modular \
  --endpoint /v1/chat/completions \
  --num-prompts 50 \
  --dataset-name arxiv-summarization \
  --arxiv-summarization-input-len 12000 \
  --max-output-len 1200

When it's done, you'll see the results printed to the terminal.

By default, it sends inference requests to localhost:8000, but you can change that with the --host and --port arguments.

If you want to save the results, add the --save-result option, which creates a JSON file in the local path with the following naming convention:

{backend}-{request_rate}qps-{model_name}-{timestamp}.json

But you can specify the file name with --result-filename and change the directory with --result-dir.

Instead of passing all these benchmark options, you can instead pass a configuration file. See Configuration file below.

Options
This list of options is not exhaustive. For more information, run max benchmark --help or see the benchmarking script source code.

Backend configuration:

--backend: Choose from modular (MAX v1/completions endpoint), modular-chat (MAX v1/chat/completions endpoint), vllm (vLLM), or trt-llm (TensorRT-LLM)

--model: Hugging Face model ID or local path

Load generation:

--num-prompts: Number of prompts to process (int, default: 500)

--request-rate: Request rate in requests/second (int, default: inf)

--seed: The random seed used to sample the dataset (int, default: 0)

Serving options

--base-url: Base URL of the API service

--endpoint: Specific API endpoint (/v1/completions or /v1/chat/completions)

--tokenizer: Hugging Face tokenizer to use (can be different from model)

--dataset-name: (Required; default:sharegpt) Specifies which type of benchmark dataset to use. This determines the dataset class and processing logic. See Datasets below.

--dataset-path: Path to a local dataset file that overrides the default dataset source for the specified dataset-name. The file format must match the expected format for the specified dataset-name (such as JSON for axolotl, JSONL for obfuscated-conversations, plain text for sonnet).

Additional options

--collect-gpu-stats: Report GPU utilization and memory consumption. Only works when running max benchmark on the same instance as the server, and only on NVIDIA GPUs.

--save-results: Saves results to a local JSON file.

--config-file: Path to a YAML file containing benchmark configuration. The configuration file is a YAML file that contains key-value pairs for all your benchmark configurations (as a replacement for individual command line options). See Configuration file below.

Output
Here's an explanation of the most important metrics printed upon completion:

Request throughput: Number of complete requests processed per second
Input token throughput: Number of input tokens processed per second
Output token throughput: Number of tokens generated per second
TTFT: Time to first token—the time from request start to first token generation
TPOT: Time per output token—the average time taken to generate each output token
ITL: Inter-token latency—the average time between consecutive token or token-chunk generations
If --collect-gpu-stats is set, you'll also see these:

GPU utilization: Percentage of time during which at least one GPU kernel is being executed
Peak GPU memory used: Peak memory usage during benchmark run
Datasets
The --dataset-name option supports several dataset names/formats you can use for benchmarking:

arxiv-summarization - Research paper summarization dataset containing academic papers with abstracts for training summarization models, from Hugging Face Datasets.

axolotl - Local dataset in Axolotl format with conversation segments labeled as human/assistant text, from Hugging Face Datasets.

code_debug - Long-context code debugging dataset containing code with multiple choice debugging questions for testing long-context understanding, from Hugging Face Datasets.

obfuscated-conversations - Local dataset with obfuscated conversation data. You must pair this with the --dataset-path option to specify the local JSONL file.

random - Synthetically generated random dataset that creates random token sequences with configurable input/output lengths and distributions.

sharegpt - Conversational dataset containing human-AI conversations for chat model evaluation, from Hugging Face Datasets.

sonnet - Poetry dataset using local text files containing poem lines, from Hugging Face Datasets.

vision-arena - Vision-language benchmark dataset containing images with associated questions for multimodal model evaluation, from Hugging Face Datasets.

You can override the default dataset source for any of these using the --dataset-path option (except for generated datasets like random), but you must always specify a --dataset-name so the tool knows how to process the dataset format.

Configuration file
The --config-file option allows you to specify a YAML file containing all your benchmark configurations, as a replacement for individual command line options. Simply define all the configuration options (corresponding to the max benchmark command line options) in a YAML file, all nested under the benchmark_config key.

Caution
In the YAML file, the properties must use snake_case names instead of using the hyphenated names from the command line options. For example, --num-prompts becomes num_prompts.

For instance, instead of specifying all configurations in the command line like this:

max benchmark \
  --model google/gemma-3-27b-it \
  --backend modular \
  --endpoint /v1/chat/completions \
  --host localhost \
  --port 8000 \
  --num-prompts 50 \
  --dataset-name arxiv-summarization \
  --arxiv-summarization-input-len 12000 \
  --max-output-len 1200

Create this configuration file:

gemma-benchmark.yaml
benchmark_config:
  model: google/gemma-3-27b-it
  backend: modular
  endpoint: /v1/chat/completions
  host: localhost
  port: 8000
  num_prompts: 50
  dataset_name: arxiv-summarization
  arxiv_summarization_input_len: 12000
  max_output_len: 1200

And then run the benchmark by passing that file:

max benchmark --config-file gemma-benchmark.yaml

For more config file examples, see our benchmark configs on GitHub.

For a walkthrough of setting up an endpoint and running a benchmark, see the quickstart guide.

max encode
Converts input text into embeddings for semantic search, text similarity, and NLP applications.

max encode [OPTIONS]

For a full list of options, run max encode --help.

Example

Basic embedding generation:

max encode \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --prompt "Convert this text into embeddings"

max generate
Generates output from a given model and prompt, without using an endpoint—primarily for debugging and testing purposes.

max generate [OPTIONS]

For a full list of options, run max generate --help.

Examples

Text generation:

max generate \
  --model google/gemma-3-12b-it \
  --prompt "Generate a story about a robot"

Text generation with controls:

max generate \
  --model google/gemma-3-12b-it \
  --max-length 1024 \
  --max-new-tokens 500 \
  --top-k 40 \
  --temperature 0.7 \
  --seed 42 \
  --prompt "Explain quantum computing"

Process an image using a vision-language model given a URL to an image:

Llama 3.2 Vision

Llama Vision models take prompts with <|image|> and <|begin_of_text|> tokens. For more information, see the Llama 3.2 Vision documentation.

max generate \
  --model meta-llama/Llama-3.2-11B-Vision-Instruct \
  --prompt "<|image|><|begin_of_text|>What is in this image?" \
  --image_url https://upload.wikimedia.org/wikipedia/commons/5/53/Almendro_en_flor_Sierras_de_Tejeda%2C_Almijara_y_Alhama.jpg \
  --max-new-tokens 100 \
  --max-batch-size 1 \
  --max-length 108172


Pixtral

Pixtral models take prompts with [IMG] tokens. For more information, see the Pixtral documentation.

max generate \
  --model mistral-community/pixtral-12b \
  --max-length 6491 \
  --image_url https://upload.wikimedia.org/wikipedia/commons/5/53/Almendro_en_flor_Sierras_de_Tejeda%2C_Almijara_y_Alhama.jpg \
  --prompt "<s>[INST]Describe the images.\n[IMG][/INST]"


You can adjust parameters like --max-batch-size and --max-length depending on your system's available resources such as GPU memory.

For more information on how to use the generate command with vision models, see Image to text.

Generation parameters
Controls for generation behavior.

Option	Description	Default	Values
--enable-constrained-decoding	Enable constrained generation	false	true|false
--enable-echo	Enable model echo	false	true|false
--image_url	URLs of images to include with prompt. Ignored if model doesn't support image inputs	[]	List of valid URLs
--rope-type	RoPE type for GGUF weights		none|normal|neox
--seed	Random seed for generation reproducibility		Integer value
--temperature	Sampling temperature for generation randomness	1.0	Float value (0.0 to 2.0)
--top-k	Limit sampling to top K tokens	255	Positive integer (1 for greedy sampling)
--chat-template	Custom chat template for the model		Valid chat template string
max list
Displays available model architectures and configurations, including:

Hugging Face model repositories
Supported encoding types
Available cache strategies
max list

This prints all the architecture information to the terminal. You can also generate a JSON output with --json flag.

max serve
Launches a model server with an OpenAI-compatible endpoint. Just specify the model as a Hugging Face model ID or a local path.

max serve [OPTIONS]

For a full list of options, run max serve --help.

For details about the endpoint APIs, see the MAX REST API reference.

Example:

max serve \
  --model google/gemma-3-12b-it \
  --devices gpu:0 \
  --max-batch-size 8 \
  --device-memory-utilization 0.9

The max CLI also supports loading custom model architectures through the --custom-architectures flag. This allows you to extend MAX's capabilities with your own model implementations:

max serve \
  --model google/gemma-3-12b-it \
  --custom-architectures path/to/module1:module1 \
  --custom-architectures path/to/module2:module2

Custom architectures
The --custom-architectures flag allows you to load custom pipeline architectures from your own Python modules. You can set the ARCHITECTURES variable containing the architecture definitions. Each entry in --custom-architectures can be specified in two formats:

A raw module name; for example: my_module.
An import path followed by a colon and the module name; for example: folder/path/to/import:my_module.
The ARCHITECTURES variable in your module should be a list of implementations that conform to the SupportedArchitecture interface. These will be registered with the MAX pipeline registry automatically.

Server configuration
Network settings for server deployment.

Option	Description	Default	Values
--host	Host address to bind the server to	localhost	IP address or hostname
--port	Port number to bind the server to	8000	Port number
Model configuration
Core settings for model loading and execution.

Option	Description	Default	Values
--custom-architectures	Load custom pipeline architectures		Module path format: folder/path/to/import:my_module
--model TEXT	Model ID or local path		Hugging Face repo ID (e.g. mistralai/Mistral-7B-v0.1) or a local path
--model-path TEXT	Model ID or local path (alternative to --model)		Hugging Face repo ID (e.g. mistralai/Mistral-7B-v0.1) or a local path
--quantization-encoding	Weight encoding type		float32|bfloat16|q4_k|q4_0|q6_k|gptq
--served-model-name	Override the default model name reported to clients (serve command only).		Any string identifier
--weight-path PATH	Custom model weights path		Valid file path (supports multiple paths via repeated flags)
Quantization encoding
When using GGUF models, quantization encoding formats are automatically detected. If no --quantization-encoding is specified, MAX Serve automatically detects and uses the first encoding option from the repository. If quantization encoding is provided, it must align with the available encoding options in the repository.

If the repository contains multiple quantization formats, specify which encoding type you want to use with the --quantization-encoding parameter.

Device configuration
Controls hardware placement and memory usage.

Option	Description	Default	Values
--devices	Target devices		cpu|gpu|gpu:{id} (e.g. gpu:0,1)
--device-specs	Specific device configuration	CPU	DeviceSpec format (e.g. DeviceSpec(id=-1, device_type='cpu'))
--device-memory-utilization	Device memory fraction	0.9	Float between 0.0 and 1.0
Performance tuning
Optimization settings for batch processing, caching, and sequence handling.

Option	Description	Default	Values
--cache-strategy	Cache strategy		naive|continuous
--kv-cache-page-size	Token count per KVCache page	128	Positive integer
--max-batch-size	Maximum cache size per batch	1	Positive integer
--max-ce-batch-size	Maximum context encoding batch size	32	Positive integer
--max-length	Maximum input sequence length	The Hugging Face model's default max length is used.	Positive integer (must be less than model's max config)
--max-new-tokens	Maximum tokens to generate	-1	Integer (-1 for model max)
--data-parallel-degree	Number of devices for data parallelism	1	Positive integer
Model state control
Options for saving or loading model states and handling external code

Option	Description	Default	Values
--force-download	Force re-download cached files	false	true|false
--trust-remote-code	Allow custom Hugging Face code	false	true|false
--allow-safetensors-weights-fp32-bf6-bidirectional-cast	Allow automatic bidirectional dtype casts between fp32 and bfloat16	false	true|false
max warm-cache
Preloads and compiles the model to optimize initialization time by:

Pre-compiling models before deployment
Warming up the Hugging Face cache
This command is useful to run before serving a model.

max warm-cache [OPTIONS]

For a full list of options, run max warm-cache --help.

Example:

max warm-cache \
  --model google/gemma-3-12b-it

The Modular Executable Format (MEF) is platform independent, but the serialized cache (MEF files) produced during compilation is platform-dependent. This is because:

Platform-dependent optimizations happen during compilation.
Fallback operations assume a particular runtime environment.
Weight transformations and hashing during MEF caching can impact performance. While efforts to improve this through weight externalization are ongoing, compiled MEF files remain platform-specific and are not generally portable.