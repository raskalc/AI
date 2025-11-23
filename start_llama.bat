set GGML_VULKAN_DEVICE=1
.\llama\llama-server.exe -m .\model.gguf --chat-template gemma -ngl 20 -c 2048
