group "default" {
    targets = [
        "py311-cuda121",
        "py311-cuda118",
        "py311-cuda124",
        "py38-rocm56",
        "py310-rocm57",
        "py310-rocm602",
        "py39-rocm60",
        "py39-rocm61",
        "py310-rocm61",
        "py39-rocm612",
        "py310-rocm612"
    ]
}

group "rocm" {
    targets = [
        "py310-rocm56",
        "py310-rocm57",
        "py310-rocm602",
        "py310-rocm60",
        "py310-rocm61",
        "py310-rocm612"
    ]
}

target "py311-cuda121" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04",
        PYTHON_VERSION = "3.11"
    }
    tags = ["madiator2011/better-base:cuda12.1"]
}

target "py311-cuda118" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04",
        PYTHON_VERSION = "3.11"
    }
    tags = ["madiator2011/better-base:cuda11.8"]
}

target "py311-cuda124" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04",
        PYTHON_VERSION = "3.11"
    }
    tags = ["madiator2011/better-base:cuda12.4"]
}

# ROCm Targets
target "py310-rocm56" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm5.6_ubuntu20.04_py3.10_pytorch_2.0.1",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm5.6"]
}

target "py310-rocm57" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm5.7"]
}

target "py310-rocm602" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.0.2_ubuntu22.04_py3.10_pytorch_2.1.2",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm6.0.2"]
}

target "py310-rocm60" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.0_ubuntu20.04_py3.10_pytorch_2.1.1",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm6.0"]
}

target "py310-rocm61" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.1_ubuntu22.04_py3.10_pytorch_2.1.2",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm6.1"]
}

target "py310-rocm612" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.1.2_ubuntu22.04_py3.10_pytorch_release-2.1.2",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-base:rocm6.1.2"]
}
