(import "ksonnet-util/kausal.libsonnet") +
{
  _config:: {
    flaskhello: {
      port: 5000,
      name: "flask-hello",
    },
  },

  local deployment = $.apps.v1.deployment,
  local container = $.core.v1.container,
  local port = $.core.v1.containerPort,
  local service = $.core.v1.service,
  local secret = $.core.v1.secret,

  flaskhello: {
    deployment: deployment.new(
      name=$._config.flaskhello.name, replicas=1,
      containers=[
        container.new($._config.flaskhello.name, "gabrielfalcao/flask-hello")
        + container.withPorts([port.new("ui", $._config.flaskhello.port)]) + container.withImagePullPolicy("Always"),
      ],
    ),
    service: $.util.serviceFor(self.deployment) + service.mixin.spec.withType("NodePort"),
    secret: secret.new(
      name=$._config.flaskhello.name, data={}) + secret.withStringData({
        username:"foo",
        password:"bar",
      })
  }
}
