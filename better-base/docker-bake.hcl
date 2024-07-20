group "default" {
    targets = ["py310-cuda121", "py310-cuda118", "py310-cuda124"]
}

target "py310-cuda121" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:cuda12.1"]
}

target "py310-cuda118" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:cuda11.8"]
}

target "py310-cuda124" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:cuda12.4"]
}
