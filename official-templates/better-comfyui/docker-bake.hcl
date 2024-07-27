group "default" {
    targets = ["full-version", "light-version", "light-experimental"]
}

target "base" {
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-base:cuda12.1",
        TORCH = "torch==2.3.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html",
        PYTHON_VERSION1 = "3.10"
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
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    tags = ["madiator2011/better-comfyui:full"]
}

target "light-version" {
    inherits = ["base"]
    args = {
        INCLUDE_MODELS = "false"
    }
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    tags = ["madiator2011/better-comfyui:light"]
}

target "light-experimental" {
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-base:light-cuda",
        TORCH = "torch==2.3.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html",
        PYTHON_VERSION1 = "3.10",
        INCLUDE_MODELS = "false"
    }
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    tags = ["madiator2011/better-comfyui:light-experimental"]
}