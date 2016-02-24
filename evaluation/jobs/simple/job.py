def execute(jobParameters):
    jobParameters.knockClient.knockOnPort(jobParameters.targetServer, jobParameters.targetPort)