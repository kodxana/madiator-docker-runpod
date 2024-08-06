group "default" {
    targets = [
        "py310-rocm56",
        "py310-rocm57",
        "py310-rocm602",
        "py310-rocm60",
        "py310-rocm61",
        "py310-rocm612"
    ]
}

# ROCm Targets
target "py310-rocm56" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm5.6_ubuntu20.04_py3.8_pytorch_2.0.1"
    }
    tags = ["madiator2011/better-base:rocm5.6"]
}

target "py310-rocm57" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm5.7_ubuntu22.04_py3.10_pytorch_2.0.1"
    }
    tags = ["madiator2011/better-base:rocm5.7"]
}

target "py310-rocm602" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.0.2_ubuntu22.04_py3.10_pytorch_2.1.2"
    }
    tags = ["madiator2011/better-base:rocm6.0.2"]
}

target "py310-rocm60" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.0_ubuntu20.04_py3.9_pytorch_2.1.1"
    }
    tags = ["madiator2011/better-base:rocm6.0"]
}

target "py310-rocm61" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.1_ubuntu22.04_py3.10_pytorch_2.1.2"
    }
    tags = ["madiator2011/better-base:rocm6.1"]
}

target "py310-rocm612" {
    contexts = {
        default = "../../container-template"
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "rocm/pytorch:rocm6.1.2_ubuntu22.04_py3.10_pytorch_release-2.1.2"
    }
    tags = ["madiator2011/better-base:rocm6.1.2"]
}
