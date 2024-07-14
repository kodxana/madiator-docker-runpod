group "default" {
    targets = ["py310-cuda121"]
}

target "py310-cuda121" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-pytorch:cuda12.1",
        TORCH = "torch==2.1.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html",
        PYTHON_VERSION = "3.10"
    }
    tags = ["madiator2011/better-everydream2:cuda12.1"]
}
