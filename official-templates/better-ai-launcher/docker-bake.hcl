group "default" {
    targets = ["better-ai-launcher"]
}

target "better-ai-launcher" {
    dockerfile = "Dockerfile"
    args = {
        BASE_IMAGE = "madiator2011/better-base:cuda12.1",
    }
    contexts = {
        scripts = "../../container-template"
        proxy = "../../container-template/proxy"
        logo = "../../container-template"
    }
    tags = ["madiator2011/better-launcher:latest"]
}