group "default" {
    targets = ["full-version", "light-version", "dev"]
}

target "base" {
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-base:cuda12.1",
        TORCH = "torch==2.3.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html",
        PYTHON_VERSION1 = "3.11"
    }
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
}

target "full-version" {
    inherits = ["base"]
    args = {
        INCLUDE_MODELS = "true"
    }
    tags = ["madiator2011/better-comfyui:full"]
}

target "light-version" {
    inherits = ["base"]
    args = {
        INCLUDE_MODELS = "false"
    }
    tags = ["madiator2011/better-comfyui:light"]
}

target "dev" {
    inherits = ["base"]
    args = {
        INCLUDE_MODELS = "false"
    }
    tags = ["madiator2011/better-comfyui:dev"]
}