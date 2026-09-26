# ECS — checklist

## Saturated (repoint lens)
- ECS task/execution-role abuse is exhaustively documented (RegisterTaskDefinition/RunTask/StartTask/
  CreateService/UpdateService incl. "reactivate dormant service with stored task role"/overrides/
  CreateTaskSet/capacity-provider/ECS Anywhere). `ecs:UpdateExpressGatewayService(taskRoleArn,executionRoleArn)`
  is a brand-new launcher construct but adds no new mechanism over the documented task-role passing =>
  NOT a distinct net-new. Skip unless Express Gateway gains a unique role-handling quirk.
