group "default" {
    targets = ["light"]
}

target "light" {
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-base:cuda12.1",
        PYTHON_VERSION = "3.11"
    }
    tags = ["madiator2011/better-forge:light"]
}