########################################
## CONFIG | Airflow Configs
########################################
airflow:
  ## if we use legacy 1.10 airflow commands
  ##
  legacyCommands: false

  ## configs for the airflow container image
  ##
  image:
    repository: apache/airflow
    tag: 2.6.3-python3.9
    pullPolicy: Always
    pullSecret: ""
    uid: 50000
    gid: 0

  ## the airflow executor type to use
  ## - allowed values: "CeleryExecutor", "KubernetesExecutor", "CeleryKubernetesExecutor"
  ## - customize the "KubernetesExecutor" pod-template with `airflow.kubernetesPodTemplate.*`
  ##
  executor: CeleryExecutor

  ## the fernet encryption key (sets `AIRFLOW__CORE__FERNET_KEY`)
  ## - [WARNING] you must change this value to ensure the security of your airflow
  ## - set `AIRFLOW__CORE__FERNET_KEY` with `airflow.extraEnv` from a Secret to avoid storing this in your values
  ## - use this command to generate your own fernet key:
  ##   python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)"
  ##
  fernetKey: "7T512UXSSmBOkpWimFHIVb8jK6lfmSAvx4mO6Arehnc="

  ## the secret_key for flask (sets `AIRFLOW__WEBSERVER__SECRET_KEY`)
  ## - [WARNING] you must change this value to ensure the security of your airflow
  ## - set `AIRFLOW__WEBSERVER__SECRET_KEY` with `airflow.extraEnv` from a Secret to avoid storing this in your values
  ##
  webserverSecretKey: "THIS IS UNSAFE!"

  ## environment variables for airflow configs
  ## - airflow env-vars are structured: "AIRFLOW__{config_section}__{config_name}"
  ## - airflow configuration reference:
  ##   https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html
  ##
  ## ____ EXAMPLE _______________
  ##   config:
  ##     # dag configs
  ##     AIRFLOW__CORE__LOAD_EXAMPLES: "False"
  ##     AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL: "30"
  ##
  ##     # email configs
  ##     AIRFLOW__EMAIL__EMAIL_BACKEND: "airflow.utils.email.send_email_smtp"
  ##     AIRFLOW__SMTP__SMTP_HOST: "smtpmail.example.com"
  ##     AIRFLOW__SMTP__SMTP_MAIL_FROM: "admin@example.com"
  ##     AIRFLOW__SMTP__SMTP_PORT: "25"
  ##     AIRFLOW__SMTP__SMTP_SSL: "False"
  ##     AIRFLOW__SMTP__SMTP_STARTTLS: "False"
  ##
  ##     # domain used in airflow emails
  ##     AIRFLOW__WEBSERVER__BASE_URL: "http://airflow.example.com"
  ##
  ##     # ether environment variables
  ##     HTTP_PROXY: "http://proxy.example.com:8080"
  ##
  config: {}

  ## a list of users to create
  ## - templates can ONLY be used in: `password`, `email`, `firstName`, `lastName`
  ## - templates used a bash-like syntax: ${MY_USERNAME}, $MY_USERNAME
  ## - templates are defined in `usersTemplates`
  ## - `role` can be a single role or a list of roles
  ##
  users:
    - username: admin
      password: admin
      role: Admin
      email: admin@example.com
      firstName: admin
      lastName: admin

  ## bash-like templates to be used in `airflow.users`
  ## - [WARNING] if a Secret or ConfigMap is missing, the sync Pod will crash
  ## - [WARNING] all keys must match the regex: ^[a-zA-Z_][a-zA-Z0-9_]*$
  ##
  ## ____ EXAMPLE _______________
  ##   usersTemplates
  ##     MY_USERNAME:
  ##       kind: configmap
  ##       name: my-configmap
  ##       key: username
  ##     MY_PASSWORD:
  ##       kind: secret
  ##       name: my-secret
  ##       key: password
  ##
  usersTemplates: {}

  ## if we create a Deployment to perpetually sync `airflow.users`
  ## - when `true`, users are updated in real-time, as ConfigMaps/Secrets change
  ## - when `true`, users changes from the WebUI will be reverted automatically
  ## - when `false`, users will only update one-time, after each `helm upgrade`
  ##
  usersUpdate: true

  ## a list airflow connections to create
  ## - templates can ONLY be used in: `host`, `login`, `password`, `schema`, `extra`
  ## - templates used a bash-like syntax: ${AWS_ACCESS_KEY} or $AWS_ACCESS_KEY
  ## - templates are defined in `connectionsTemplates`
  ##
  ## ____ EXAMPLE _______________
  ##   connections:
  ##     - id: my_aws
  ##       type: aws
  ##       description: my AWS connection
  ##       extra: |-
  ##         { "aws_access_key_id": "${AWS_KEY_ID}",
  ##           "aws_secret_access_key": "${AWS_ACCESS_KEY}",
  ##           "region_name":"eu-central-1" }
  ##
  connections: []

  ## bash-like templates to be used in `airflow.connections`
  ## - see docs for `airflow.usersTemplates`
  ##
  connectionsTemplates: {}

  ## if we create a Deployment to perpetually sync `airflow.connections`
  ## - see docs for `airflow.usersUpdate`
  ##
  connectionsUpdate: true

  ## a list airflow variables to create
  ## - templates can ONLY be used in: `value`
  ## - templates used a bash-like syntax: ${MY_VALUE} or $MY_VALUE
  ## - templates are defined in `connectionsTemplates`
  ##
  ## ____ EXAMPLE _______________
  ##   variables:
  ##     - key: "var_1"
  ##       value: "my_value_1"
  ##     - key: "var_2"
  ##       value: "my_value_2"
  ##
  variables: []

  ## bash-like templates to be used in `airflow.variables`
  ## - see docs for `airflow.usersTemplates`
  ##
  variablesTemplates: {}

  ## if we create a Deployment to perpetually sync `airflow.variables`
  ## - see docs for `airflow.usersUpdate`
  ##
  variablesUpdate: true

  ## a list airflow pools to create
  ##
  ## ____ EXAMPLE _______________
  ##   pools:
  ##     - name: "pool_1"
  ##       description: "example pool with 5 slots"
  ##       slots: 5
  ##     - name: "pool_2"
  ##       description: "example pool with 2 cron policies"
  ##       slots: 0
  ##       ## if deferred tasks count towards the slot limit, requires airflow 2.7.0+ (default: false)
  ##       include_deferred: false
  ##       ## at each sync interval, the policy with the most recently past `recurrence` is applied
  ##       policies:
  ##         - name: "scale up at 7pm UTC"
  ##           slots: 50
  ##           recurrence: "0 19 * * *"
  ##         - name: "scale down at 6am UTC"
  ##           slots: 10
  ##           recurrence: "0 6 * * *"
  ##
  pools: []

  ## if we create a Deployment to perpetually sync `airflow.pools`
  ## - see docs for `airflow.usersUpdate`
  ##
  poolsUpdate: true

  ## default nodeSelector for airflow Pods (is overridden by pod-specific values)
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  defaultNodeSelector: {}

  ## default affinity configs for airflow Pods (is overridden by pod-specific values)
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  defaultAffinity: {}

  ## default toleration configs for airflow Pods (is overridden by pod-specific values)
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  defaultTolerations: []

  ## default securityContext configs for airflow Pods (is overridden by pod-specific values)
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  defaultSecurityContext:
    ## sets the filesystem owner group of files/folders in mounted volumes
    ## this does NOT give root permissions to Pods, only the "root" group
    fsGroup: 0

  ## extra annotations for airflow Pods
  ##
  podAnnotations: {}

  ## extra pip packages to install in airflow Pods
  ##
  ## ____ EXAMPLE _______________
    extraPipPackages:
      - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## pip packages that are protected from upgrade/downgrade by `extraPipPackages`
  ## - [WARNING] Pods will fail to start if `extraPipPackages` would cause these packages to change versions
  ##
  protectedPipPackages:
    - "apache-airflow"

  ## extra environment variables for the airflow Pods
  ## - spec for EnvVar:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#envvar-v1-core
  ##
  extraEnv: []

  ## extra containers for the airflow Pods
  ## - spec for Container:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#container-v1-core
  ##
  extraContainers: []

  ## extra VolumeMounts for the airflow Pods
  ## - spec for VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the airflow Pods
  ## - spec for Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

  ## kubernetes cluster domain name
  ## - configured in the kubelet with `--cluster-domain` flag (deprecated):
  ##   https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/
  ## - or configured in the kubelet with configuration file `clusterDomain` option:
  ##   https://kubernetes.io/docs/tasks/administer-cluster/kubelet-config-file/
  ##
  clusterDomain: "cluster.local"

  ########################################
  ## FILE | airflow_local_settings.py
  ########################################
  ##
  localSettings:
    ## the full content of the `airflow_local_settings.py` file (as a string)
    ## - docs for airflow cluster policies:
    ##   https://airflow.apache.org/docs/apache-airflow/stable/concepts/cluster-policies.html
    ##
    ## ____ EXAMPLE _______________
    ##    stringOverride: |
    ##      # use a custom `xcom_sidecar` image for KubernetesPodOperator()
    ##      from airflow.kubernetes.pod_generator import PodDefaults
    ##      PodDefaults.SIDECAR_CONTAINER.image = "gcr.io/PROJECT-ID/custom-sidecar-image"
    ##
    stringOverride: ""

    ## the name of a Secret containing a `airflow_local_settings.py` key
    ## - if set, this disables `airflow.localSettings.stringOverride`
    ##
    existingSecret: ""

  ########################################
  ## FILE | pod_template.yaml
  ########################################
  ## - generates a file for `AIRFLOW__KUBERNETES__POD_TEMPLATE_FILE`
  ## - the `dags.gitSync` values will create a git-sync init-container in the pod
  ## - the `airflow.extraPipPackages` will NOT be installed
  ##
  kubernetesPodTemplate:
    ## the full content of the pod-template file (as a string)
    ## - [WARNING] all other `kubernetesPodTemplate.*` are disabled when this is set
    ## - docs for pod-template file:
    ##   https://airflow.apache.org/docs/apache-airflow/stable/executor/kubernetes.html#pod-template-file
    ##
    ## ____ EXAMPLE _______________
    ##   stringOverride: |-
    ##     apiVersion: v1
    ##     kind: Pod
    ##     spec: ...
    ##
    stringOverride: ""

    ## resource requests/limits for the Pod template "base" container
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the nodeSelector configs for the Pod template
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the Pod template
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the Pod template
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## labels for the Pod template
    ##
    podLabels: {}

    ## annotations for the Pod template
    ##
    podAnnotations: {}

    ## the security context for the Pod template
    ## - spec for PodSecurityContext:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
    ##
    securityContext: {}

    ## the shareProcessNamespace config for the Pod template
    ## - docs for shareProcessNamespace:
    ##   https://kubernetes.io/docs/tasks/configure-pod-container/share-process-namespace/
    ##
    shareProcessNamespace: false

    ## extra pip packages to install in the Pod template
    ##
    ## ____ EXAMPLE _______________
    ##   extraPipPackages:
    ##     - "SomeProject==1.0.0"
    ##
    extraPipPackages: []

    ## extra containers for the pod template
    ## - spec for Container:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#container-v1-core
    ##
    extraContainers: []

    ## extra init-containers for the Pod template
    ## - spec of Container:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#container-v1-core
    ##
    extraInitContainers: []

    ## extra VolumeMounts for the Pod template
    ## - spec for VolumeMount:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
    ##
    extraVolumeMounts: []

    ## extra Volumes for the Pod template
    ## - spec for Volume:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
    ##
    extraVolumes: []

  ########################################
  ## COMPONENT | db-migrations Deployment
  ########################################
  dbMigrations:
    ## if the db-migrations Deployment/Job is created
    ## - [WARNING] if `false`, you have to MANUALLY run `airflow db upgrade` when required
    ##
    enabled: true

    ## if a post-install helm Job should be used (instead of a Deployment)
    ## - [WARNING] setting `true` will NOT work with the helm `--wait` flag,
    ##   this is because post-install helm Jobs run AFTER the main resources become Ready,
    ##   which will cause a deadlock, as other resources require db-migrations to become Ready
    ##
    runAsJob: false

    ## resource requests/limits for the db-migrations Pods
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the nodeSelector configs for the db-migrations Pods
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the db-migrations Pods
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the db-migrations Pods
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## the security context for the db-migrations Pods
    ## - spec for PodSecurityContext:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
    ##
    securityContext: {}

    ## Labels for the db-migrations Deployment
    ##
    labels: {}

    ## Pod labels for the db-migrations Deployment
    ##
    podLabels: {}

    ## annotations for the db-migrations Deployment/Job
    ##
    annotations: {}

    ## Pod annotations for the db-migrations Deployment/Job
    ##
    podAnnotations: {}

    ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
    ##
    safeToEvict: true

    ## the number of seconds between checks for unapplied db migrations
    ## - only applies if `airflow.dbMigrations.runAsJob` is `false`
    ##
    checkInterval: 300

  ########################################
  ## COMPONENT | Sync Deployments
  ########################################
  ## - used by the Deployments/Jobs used by `airflow.{connections,pools,users,variables}`
  ##
  sync:
    ## resource requests/limits for the sync Pods
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the nodeSelector configs for the sync Pods
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the sync Pods
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the sync Pods
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## the security context for the sync Pods
    ## - spec for PodSecurityContext:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
    ##
    securityContext: {}

    ## Labels for the sync Deployments/Jobs
    ##
    labels: {}

    ## Pod labels for the sync Deployments/Jobs
    ##
    podLabels: {}

    ## annotations for the sync Deployments/Jobs
    ##
    annotations: {}

    ## Pod annotations for the sync Deployments/Jobs
    ##
    podAnnotations: {}

    ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
    ##
    safeToEvict: true

###################################
## COMPONENT | Airflow Scheduler
###################################
scheduler:
  ## the number of scheduler Pods to run
  ## - if you set this >1 we recommend defining a `scheduler.podDisruptionBudget`
  ##
  replicas: 1

  ## resource requests/limits for the scheduler Pod
  ## - spec of ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the scheduler Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the scheduler Pods
  ## - spec of Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the scheduler Pods
  ## - spec of Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the scheduler Pods
  ## - spec of PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## labels for the scheduler Deployment
  ##
  labels: {}

  ## Pod labels for the scheduler Deployment
  ##
  podLabels: {}

  ## annotations for the scheduler Deployment
  ##
  annotations: {}

  ## Pod annotations for the scheduler Deployment
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the scheduler
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the scheduler
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the scheduler
    ##
    maxUnavailable: ""

    ## the minimum available pods/percentage for the scheduler
    ##
    minAvailable: ""

  ## configs for the log-cleanup sidecar of the scheduler
  ## - helps prevent excessive log buildup by regularly deleting old files
  ##
  logCleanup:
    ## if the log-cleanup sidecar is enabled
    ## - [WARNING] must be disabled if `logs.persistence.enabled` is `true`
    ##
    enabled: true

    ## resource requests/limits for the log-cleanup container
    ## - spec of ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the number of minutes to retain log files (by last-modified time)
    ##
    retentionMinutes: 21600

    ## the number of seconds between each check for files to delete
    ##
    intervalSeconds: 900

  ## sets `airflow --num_runs` parameter used to run the airflow scheduler
  ##
  numRuns: -1

  ## configs for the scheduler Pods' liveness probe
  ## - "unhealthy" means the SchedulerJob has not had a heartbeat for
  ##   AIRFLOW__SCHEDULER__SCHEDULER_HEALTH_CHECK_THRESHOLD seconds
  ## - `periodSeconds` x `failureThreshold` = max seconds a scheduler can be in an "unhealthy" state
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 30
    timeoutSeconds: 60
    failureThreshold: 5

    ## configs for an additional check that ensures tasks are being created by the scheduler
    ## - this check works by ensuring that the most recent LocalTaskJob had a `start_date` no more than
    ##   `taskCreationCheck.thresholdSeconds` seconds ago
    ## - this check is useful because the scheduler can deadlock with a heartbeat, but not be scheduling new tasks:
    ##   https://github.com/apache/airflow/issues/7935 - patched in airflow `2.0.2`
    ##   https://github.com/apache/airflow/issues/15938 - patched in airflow `2.1.1`
    ##
    taskCreationCheck:
      ## if the task creation check is enabled
      ##
      enabled: false

      ## the maximum number of seconds since the start_date of the most recent LocalTaskJob
      ## - [WARNING] must be AT LEAST equal to your shortest DAG schedule_interval
      ## - [WARNING] DummyOperator tasks will NOT be seen by this probe
      ##
      thresholdSeconds: 300

      ## minimum number of seconds the scheduler must have run before the task creation check begins
      ## - [WARNING] must be long enough for the scheduler to boot and create a task
      ##
      schedulerAgeBeforeCheck: 180

  ## extra pip packages to install in the scheduler Pods
  ##
  ## ____ EXAMPLE _______________
  ##   extraPipPackages:
  ##     - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## extra VolumeMounts for the scheduler Pods
  ## - spec of VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the scheduler Pods
  ## - spec of Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

  ## extra init containers to run in the scheduler Pods
  ## - spec of Container:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#container-v1-core
  ##
  extraInitContainers: []

###################################
## COMPONENT | Airflow Webserver
###################################
web:
  ########################################
  ## FILE | webserver_config.py
  ########################################
  ##
  webserverConfig:
    ## if the `webserver_config.py` file is mounted
    ## - set to false if you wish to mount your own `webserver_config.py` file
    ##
    enabled: true

    ## the full content of the `webserver_config.py` file (as a string)
    ## - docs for Flask-AppBuilder security configs:
    ##   https://flask-appbuilder.readthedocs.io/en/latest/security.html
    ##
    ## ____ EXAMPLE _______________
    ##   stringOverride: |
    ##     from airflow import configuration as conf
    ##     from flask_appbuilder.security.manager import AUTH_DB
    ##
    ##     # the SQLAlchemy connection string
    ##     SQLALCHEMY_DATABASE_URI = conf.get('core', 'SQL_ALCHEMY_CONN')
    ##
    ##     # use embedded DB for auth
    ##     AUTH_TYPE = AUTH_DB
    ##
    stringOverride: ""

    ## the name of a Secret containing a `webserver_config.py` key
    ##
    existingSecret: ""

  ## the number of web Pods to run
  ## - if you set this >1 we recommend defining a `web.podDisruptionBudget`
  ##
  replicas: 1

  ## resource requests/limits for the web Pod
  ## - spec for ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the web Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the web Pods
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the web Pods
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the web Pods
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## labels for the web Deployment
  ##
  labels: {}

  ## Pod labels for the web Deployment
  ##
  podLabels: {}

  ## annotations for the web Deployment
  ##
  annotations: {}

  ## Pod annotations for the web Deployment
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the web Deployment
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the web Deployment
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the web Deployment
    ##
    maxUnavailable: ""

    ## the minimum available pods/percentage for the web Deployment
    ##
    minAvailable: ""

  ## configs for the Service of the web Pods
  ##
  service:
    annotations: {}
    sessionAffinity: "None"
    sessionAffinityConfig: {}
    type: NodePort
    externalPort: 8080
    loadBalancerIP: ""
    loadBalancerSourceRanges: []
    nodePort:
      http: ""

  ## configs for the web Pods' readiness probe
  ##
  readinessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6

  ## configs for the web Pods' liveness probe
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6

  ## extra pip packages to install in the web Pods
  ##
  ## ____ EXAMPLE _______________
  ##   extraPipPackages:
  ##     - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## extra VolumeMounts for the web Pods
  ## - spec for VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the web Pods
  ## - spec for Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

###################################
## COMPONENT | Airflow Workers
###################################
workers:
  ## if the airflow workers StatefulSet should be deployed
  ##
  enabled: true

  ## the number of worker Pods to run
  ## - if you set this >1 we recommend defining a `workers.podDisruptionBudget`
  ## - this is the minimum when `workers.autoscaling.enabled` is true
  ##
  replicas: 1

  ## resource requests/limits for the worker Pod
  ## - spec for ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the worker Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the worker Pods
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the worker Pods
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the worker Pods
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## labels for the worker StatefulSet
  ##
  labels: {}

  ## Pod labels for the worker StatefulSet
  ##
  podLabels: {}

  ## annotations for the worker StatefulSet
  ##
  annotations: {}

  ## Pod annotations for the worker StatefulSet
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the worker StatefulSet
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the worker StatefulSet
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the worker StatefulSet
    ##
    maxUnavailable: ""

    ## the minimum available pods/percentage for the worker StatefulSet
    ##
    minAvailable: ""

  ## configs for the HorizontalPodAutoscaler of the worker Pods
  ## - [WARNING] if using git-sync, ensure `dags.gitSync.resources` is set
  ## - [WARNING] if using worker log-cleanup, ensure `workers.logCleanup.resources` is set
  ##
  ## ____ EXAMPLE _______________
  ##   autoscaling:
  ##     enabled: true
  ##     maxReplicas: 16
  ##     metrics:
  ##     - type: Resource
  ##       resource:
  ##         name: memory
  ##         target:
  ##           type: Utilization
  ##           averageUtilization: 80
  ##
  autoscaling:
    enabled: false
    maxReplicas: 2
    metrics: []

    ## the `apiVersion` to use for HorizontalPodAutoscaler resources
    ## - for Kubernetes 1.23 and later: "autoscaling/v2"
    ## - for Kubernetes 1.22 and before: "autoscaling/v2beta2"
    ##
    apiVersion: autoscaling/v2

  ## configs for the celery worker Pods
  ##
  celery:
    ## if celery worker Pods are gracefully terminated
    ## - consider defining a `workers.podDisruptionBudget` to prevent there not being
    ##   enough available workers during graceful termination waiting periods
    ##
    ## graceful termination process:
    ##  1. prevent worker accepting new tasks
    ##  2. wait AT MOST `workers.celery.gracefullTerminationPeriod` for tasks to finish
    ##  3. send SIGTERM to worker
    ##  4. wait AT MOST `workers.terminationPeriod` for kill to finish
    ##  5. send SIGKILL to worker
    ##
    gracefullTermination: false

    ## how many seconds to wait for tasks to finish before SIGTERM of the celery worker
    ##
    gracefullTerminationPeriod: 600

  ## how many seconds to wait after SIGTERM before SIGKILL of the celery worker
  ## - [WARNING] tasks that are still running during SIGKILL will be orphaned, this is important
  ##   to understand with KubernetesPodOperator(), as Pods may continue running
  ##
  terminationPeriod: 60

  ## configs for the log-cleanup sidecar of the worker Pods
  ## - helps prevent excessive log buildup by regularly deleting old files
  ##
  logCleanup:
    ## if the log-cleanup sidecar is enabled
    ## - [WARNING] must be disabled if `logs.persistence.enabled` is `true`
    ##
    enabled: true

    ## resource requests/limits for the log-cleanup container
    ## - spec of ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the number of minutes to retain log files (by last-modified time)
    ##
    retentionMinutes: 21600

    ## the number of seconds between each check for files to delete
    ##
    intervalSeconds: 900

  ## configs for the worker Pods' liveness probe
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 30
    timeoutSeconds: 60
    failureThreshold: 5

  ## extra pip packages to install in the worker Pod
  ##
  ## ____ EXAMPLE _______________
  ##   extraPipPackages:
  ##     - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## extra VolumeMounts for the worker Pods
  ## - spec for VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the worker Pods
  ## - spec for Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

###################################
## COMPONENT | Triggerer
###################################
triggerer:
  ## if the airflow triggerer should be deployed
  ## - [WARNING] the triggerer component was added in airflow 2.2.0
  ## - [WARNING] if `airflow.legacyCommands` is `true` the triggerer will NOT be deployed
  ##
  enabled: true

  ## the number of triggerer Pods to run
  ## - if you set this >1 we recommend defining a `triggerer.podDisruptionBudget`
  ##
  replicas: 1

  ## resource requests/limits for the triggerer Pods
  ## - spec for ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the triggerer Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the triggerer Pods
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the triggerer Pods
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the triggerer Pods
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## labels for the triggerer Deployment
  ##
  labels: {}

  ## Pod labels for the triggerer Deployment
  ##
  podLabels: {}

  ## annotations for the triggerer Deployment
  ##
  annotations: {}

  ## Pod annotations for the triggerer Deployment
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the triggerer Deployment
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the triggerer Deployment
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the triggerer Deployment
    ##
    maxUnavailable: ""

    ## the minimum available pods/percentage for the triggerer Deployment
    ##
    minAvailable: ""

  ## maximum number of triggers each triggerer will run at once (sets `AIRFLOW__TRIGGERER__DEFAULT_CAPACITY`)
  ##
  capacity: 1000

  ## configs for the triggerer Pods' liveness probe
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 30
    timeoutSeconds: 60
    failureThreshold: 5

  ## extra pip packages to install in the triggerer Pod
  ##
  ## ____ EXAMPLE _______________
  ##   extraPipPackages:
  ##     - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## extra VolumeMounts for the triggerer Pods
  ## - spec for VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the triggerer Pods
  ## - spec for Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

###################################
## COMPONENT | Flower
###################################
flower:
  ## if the airflow flower UI should be deployed
  ##
  enabled: true

  ## the number of flower Pods to run
  ## - if you set this >1 we recommend defining a `flower.podDisruptionBudget`
  ##
  replicas: 1

  ## resource requests/limits for the flower Pod
  ## - spec for ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the flower Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the flower Pods
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the flower Pods
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the flower Pods
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## labels for the flower Deployment
  ##
  labels: {}

  ## Pod labels for the flower Deployment
  ##
  podLabels: {}

  ## annotations for the flower Deployment
  ##
  annotations: {}

  ## Pod annotations for the flower Deployment
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the flower Deployment
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the flower Deployment
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the flower Deployment
    ##
    maxUnavailable: ""

    ## the minimum available pods/percentage for the flower Deployment
    ##
    minAvailable: ""

  ## the name of a pre-created secret containing the basic authentication value for flower
  ## - this will override any value of `config.AIRFLOW__CELERY__FLOWER_BASIC_AUTH`
  ##
  basicAuthSecret: ""

  ## the key within `flower.basicAuthSecret` containing the basic authentication string
  ##
  basicAuthSecretKey: ""

  ## configs for the Service of the flower Pods
  ##
  service:
    annotations: {}
    type: ClusterIP
    externalPort: 5555
    loadBalancerIP: ""
    loadBalancerSourceRanges: []
    nodePort:
      http:

  ## configs for the flower Pods' readinessProbe probe
  ##
  readinessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6

  ## configs for the flower Pods' liveness probe
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 10
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 6

  ## extra pip packages to install in the flower Pod
  ##
  ## ____ EXAMPLE _______________
  ##   extraPipPackages:
  ##     - "SomeProject==1.0.0"
  ##
  extraPipPackages: []

  ## extra VolumeMounts for the flower Pods
  ## - spec for VolumeMount:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volumemount-v1-core
  ##
  extraVolumeMounts: []

  ## extra Volumes for the flower Pods
  ## - spec for Volume:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#volume-v1-core
  ##
  extraVolumes: []

###################################
## CONFIG | Airflow Logs
###################################
logs:
  ## the airflow logs folder
  ##
  path: /opt/airflow/logs

  ## configs for the logs PVC
  ##
  persistence:
    ## if a persistent volume is mounted at `logs.path`
    ##
    enabled: false

    ## the name of an existing PVC to use
    ##
    existingClaim: ""

    ## sub-path under `logs.persistence.existingClaim` to use
    ##
    subPath: ""

    ## the name of the StorageClass used by the PVC
    ## - if set to "", then `PersistentVolumeClaim/spec.storageClassName` is omitted
    ## - if set to "-", then `PersistentVolumeClaim/spec.storageClassName` is set to ""
    ##
    storageClass: ""

    ## the access mode of the PVC
    ## - [WARNING] must be "ReadWriteMany" or airflow pods will fail to start
    ##
    accessMode: ReadWriteMany

    ## the size of PVC to request
    ##
    size: 1Gi

###################################
## CONFIG | Airflow DAGs
###################################
dags:
  ## the airflow dags folder
  ##
  path: /opt/airflow/dags

  ## configs for the dags PVC
  ##
  persistence:
    ## if a persistent volume is mounted at `dags.path`
    ##
    enabled: false

    ## the name of an existing PVC to use
    ##
    existingClaim: ""

    ## sub-path under `dags.persistence.existingClaim` to use
    ##
    subPath: ""

    ## the name of the StorageClass used by the PVC
    ## - if set to "", then `PersistentVolumeClaim/spec.storageClassName` is omitted
    ## - if set to "-", then `PersistentVolumeClaim/spec.storageClassName` is set to ""
    ##
    storageClass: ""

    ## the access mode of the PVC
    ## - [WARNING] must be "ReadOnlyMany" or "ReadWriteMany" otherwise airflow pods will fail to start
    ##
    accessMode: ReadOnlyMany

    ## the size of PVC to request
    ##
    size: 1Gi

  ## configs for the git-sync sidecar (https://github.com/kubernetes/git-sync)
  ##
  gitSync:
    ## if the git-sync sidecar container is enabled
    ##
    enabled: false

    ## the git-sync container image
    ##
    image:
      repository: registry.k8s.io/git-sync/git-sync
      tag: v3.6.5
      pullPolicy: Always
      uid: 65533
      gid: 65533

    ## resource requests/limits for the git-sync container
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the url of the git repo
    ##
    ## ____ EXAMPLE _______________
    ##   # https git repo
    ##   repo: "https://github.com/USERNAME/REPOSITORY.git"
    ##
    ## ____ EXAMPLE _______________
    ##   # ssh git repo
    ##   repo: "git@github.com:USERNAME/REPOSITORY.git"
    ##
    repo: ""

    ## the sub-path within your repo where dags are located
    ## - only dags under this path within your repo will be seen by airflow,
    ##   (note, the full repo will still be cloned)
    ##
    repoSubPath: ""

    ## the git branch to check out
    ##
    branch: master

    ## the git revision (tag or hash) to check out
    ##
    revision: HEAD

    ## shallow clone with a history truncated to the specified number of commits
    ##
    depth: 1

    ## the number of seconds between syncs
    ##
    syncWait: 60

    ## the max number of seconds allowed for a complete sync
    ##
    syncTimeout: 120

    ## the git submodule behavior
    ## - allowed values: "recursive", "shallow", "off"
    ##
    submodules: recursive

    ## the name of a pre-created Secret with git http credentials
    ##
    httpSecret: ""

    ## the key in `dags.gitSync.httpSecret` with your git username
    ##
    httpSecretUsernameKey: username

    ## the key in `dags.gitSync.httpSecret` with your git password/token
    ##
    httpSecretPasswordKey: password

    ## the name of a pre-created Secret with git ssh credentials
    ##
    sshSecret: ""

    ## the key in `dags.gitSync.sshSecret` with your ssh-key file
    ##
    sshSecretKey: id_rsa

    ## the string value of a "known_hosts" file (for SSH only)
    ## - [WARNING] known_hosts verification will be disabled if left empty, making you more
    ##   vulnerable to repo spoofing attacks
    ##
    ## ____ EXAMPLE _______________
    ##   sshKnownHosts: |-
    ##     <HOST_NAME> ssh-rsa <HOST_KEY>
    ##
    sshKnownHosts: ""

    ## the number of consecutive failures allowed before aborting
    ##  - the first sync must succeed
    ##  - a value of -1 will retry forever after the initial sync
    ##
    maxFailures: 0

###################################
## CONFIG | Kubernetes Ingress
###################################
ingress:
  ## if we should deploy Ingress resources
  ##
  enabled: false

  ## the `apiVersion` to use for Ingress resources
  ## - for Kubernetes 1.19 and later: "networking.k8s.io/v1"
  ## - for Kubernetes 1.18 and before: "networking.k8s.io/v1beta1"
  ##
  apiVersion: networking.k8s.io/v1

  ## configs for the Ingress of the web Service
  ##
  web:
    ## annotations for the web Ingress
    ##
    annotations: {}

    ## additional labels for the web Ingress
    ##
    labels: {}

    ## the path for the web Ingress
    ## - [WARNING] do NOT include the trailing slash (for root, set an empty string)
    ##
    ## ____ EXAMPLE _______________
    ##   # webserver URL: http://example.com/airflow
    ##   path: "/airflow"
    ##
    path: ""

    ## the hostname for the web Ingress
    ##
    host: ""

    ## the Ingress Class for the web Ingress
    ## - [WARNING] requires Kubernetes 1.18 or later, use "kubernetes.io/ingress.class" annotation for older versions
    ##
    ingressClassName: ""

    ## configs for web Ingress TLS
    ##
    tls:
      ## enable TLS termination for the web Ingress
      ##
      enabled: false

      ## the name of a pre-created Secret containing a TLS private key and certificate
      ##
      secretName: ""

    ## http paths to add to the web Ingress before the default path
    ##
    ## ____ EXAMPLE _______________
    ##   precedingPaths:
    ##     - path: "/*"
    ##       serviceName: "my-service"
    ##       servicePort: "port-name"
    ##
    precedingPaths: []

    ## http paths to add to the web Ingress after the default path
    ##
    ## ____ EXAMPLE _______________
    ##   succeedingPaths:
    ##     - path: "/extra-service"
    ##       serviceName: "my-service"
    ##       servicePort: "port-name"
    ##
    succeedingPaths: []

  ## configs for the Ingress of the flower Service
  ##
  flower:
    ## annotations for the flower Ingress
    ##
    annotations: {}

    ## additional labels for the flower Ingress
    ##
    labels: {}

    ## the path for the flower Ingress
    ## - [WARNING] do NOT include the trailing slash (for root, set an empty string)
    ##
    ## ____ EXAMPLE _______________
    ##   # flower URL: http://example.com/airflow/flower
    ##   path: "/airflow/flower"
    ##
    path: ""

    ## the hostname for the flower Ingress
    ##
    host: ""

    ## the Ingress Class for the flower Ingress
    ## - [WARNING] requires Kubernetes 1.18 or later, use "kubernetes.io/ingress.class" annotation for older versions
    ##
    ingressClassName: ""

    ## configs for flower Ingress TLS
    ##
    tls:
      ## enable TLS termination for the flower Ingress
      ##
      enabled: false

      ## the name of a pre-created Secret containing a TLS private key and certificate
      ##
      secretName: ""

    ## http paths to add to the flower Ingress before the default path
    ##
    ## ____ EXAMPLE _______________
    ##   precedingPaths:
    ##     - path: "/*"
    ##       serviceName: "my-service"
    ##       servicePort: "port-name"
    ##
    precedingPaths: []

    ## http paths to add to the flower Ingress after the default path
    ##
    ## ____ EXAMPLE _______________
    ##   succeedingPaths:
    ##     - path: "/extra-service"
    ##       serviceName: "my-service"
    ##       servicePort: "port-name"
    ##
    succeedingPaths: []

###################################
## CONFIG | Kubernetes RBAC
###################################
rbac:
  ## if Kubernetes RBAC resources are created
  ## - these allow the service account to create/delete Pods in the airflow namespace,
  ##   which is required for the KubernetesPodOperator() to function
  ##
  create: true

  ## if the created RBAC Role has GET/LIST on Event resources
  ## - this is needed for KubernetesPodOperator() to use `log_events_on_failure=True`
  ##
  events: true

###################################
## CONFIG | Kubernetes ServiceAccount
###################################
serviceAccount:
  ## if a Kubernetes ServiceAccount is created
  ## - if `false`, you must create the service account outside this chart with name: `serviceAccount.name`
  ##
  create: true

  ## the name of the ServiceAccount
  ## - by default the name is generated using the `airflow.serviceAccountName` template in `_helpers/common.tpl`
  ##
  name: ""

  ## annotations for the ServiceAccount
  ##
  ## ____ EXAMPLE _______________
  ##   # EKS - IAM Roles for Service Accounts
  ##   annotations:
  ##     eks.amazonaws.com/role-arn: "arn:aws:iam::XXXXXXXXXX:role/<<MY-ROLE-NAME>>"
  ##
  ## ____ EXAMPLE _______________
  ##   # GKE - WorkloadIdentity
  ##   annotations:
  ##     iam.gke.io/gcp-service-account: "<<GCP_SERVICE>>@<<GCP_PROJECT>>.iam.gserviceaccount.com"
  ##
  annotations: {}

###################################
## CONFIG | Kubernetes Extra Manifests
###################################
## a list of extra Kubernetes manifests that will be deployed alongside the chart
## - helm templates within these strings will be rendered
##
## ____ EXAMPLE _______________
##   extraManifests:
##     - |
##       apiVersion: v1
##       kind: Secret
##       metadata:
##         name: airflow-postgres
##       data:
##         postgresql-password: {{ `password1` | b64enc | quote }}
##     - |
##       apiVersion: apps/v1
##       kind: Deployment
##       metadata:
##         name: {{ include "airflow.fullname" . }}-busybox
##         labels:
##           app: {{ include "airflow.labels.app" . }}
##           component: busybox
##           chart: {{ include "airflow.labels.chart" . }}
##           release: {{ .Release.Name }}
##           heritage: {{ .Release.Service }}
##       spec:
##         replicas: 1
##         selector:
##           matchLabels:
##             app: {{ include "airflow.labels.app" . }}
##             component: busybox
##             release: {{ .Release.Name }}
##         template:
##           metadata:
##             labels:
##               app: {{ include "airflow.labels.app" . }}
##               component: busybox
##               release: {{ .Release.Name }}
##           spec:
##             containers:
##               - name: busybox
##                 image: busybox:1.35
##                 command:
##                   - "/bin/sh"
##                   - "-c"
##                 args:
##                   - |
##                     ## to break the infinite loop when we receive SIGTERM
##                     trap "exit 0" SIGTERM;
##                     ## keep the container running (so people can `kubectl exec -it` into it)
##                     while true; do
##                       echo "I am alive...";
##                       sleep 30;
##                     done
##
extraManifests: []

###################################
## DATABASE | PgBouncer
###################################
pgbouncer:
  ## if the pgbouncer Deployment is created
  ##
  enabled: true

  ## configs for the pgbouncer container image
  ##
  image:
    repository: ghcr.io/airflow-helm/pgbouncer
    tag: 1.18.0-patch.1
    pullPolicy: Always
    uid: 1001
    gid: 1001

  ## resource requests/limits for the pgbouncer Pods
  ## - spec for ResourceRequirements:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
  ##
  resources: {}

  ## the nodeSelector configs for the pgbouncer Pods
  ## - docs for nodeSelector:
  ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
  ##
  nodeSelector: {}

  ## the affinity configs for the pgbouncer Pods
  ## - spec for Affinity:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
  ##
  affinity: {}

  ## the toleration configs for the pgbouncer Pods
  ## - spec for Toleration:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
  ##
  tolerations: []

  ## the security context for the pgbouncer Pods
  ## - spec for PodSecurityContext:
  ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core
  ##
  securityContext: {}

  ## Labels for the pgbouncer Deployment
  ##
  labels: {}

  ## Pod labels for the pgbouncer Deployment
  ##
  podLabels: {}

  ## annotations for the pgbouncer Deployment
  ##
  annotations: {}

  ## Pod annotations for the pgbouncer Deployment
  ##
  podAnnotations: {}

  ## if we add the annotation: "cluster-autoscaler.kubernetes.io/safe-to-evict" = "true"
  ##
  safeToEvict: true

  ## configs for the PodDisruptionBudget of the pgbouncer Deployment
  ##
  podDisruptionBudget:
    ## if a PodDisruptionBudget resource is created for the pgbouncer Deployment
    ##
    enabled: false

    ## the `apiVersion` to use for PodDisruptionBudget resources
    ## - for Kubernetes 1.21 and later: "policy/v1"
    ## - for Kubernetes 1.20 and before: "policy/v1beta1"
    ##
    apiVersion: policy/v1

    ## the maximum unavailable pods/percentage for the pgbouncer Deployment
    ##
    maxUnavailable:

    ## the minimum available pods/percentage for the pgbouncer Deployment
    ##
    minAvailable:

  ## configs for the pgbouncer Pods' liveness probe
  ##
  livenessProbe:
    enabled: true
    initialDelaySeconds: 5
    periodSeconds: 30
    timeoutSeconds: 60
    failureThreshold: 3

  ## configs for the pgbouncer Pods' startup probe
  ##
  startupProbe:
    enabled: true
    initialDelaySeconds: 5
    periodSeconds: 10
    timeoutSeconds: 15
    failureThreshold: 30

  ## the maximum number of seconds to wait for queries upon pod termination, before force killing
  ##
  terminationGracePeriodSeconds: 120

  ## sets pgbouncer config: `auth_type`
  ##
  authType: md5

  ## sets pgbouncer config: `max_client_conn`
  ##
  maxClientConnections: 1000

  ## sets pgbouncer config: `default_pool_size`
  ##
  poolSize: 20

  ## sets pgbouncer config: `log_disconnections`
  ##
  logDisconnections: 0

  ## sets pgbouncer config: `log_connections`
  ##
  logConnections: 0

  ## ssl configs for: clients -> pgbouncer
  ##
  clientSSL:
    ## sets pgbouncer config: `client_tls_sslmode`
    ##
    mode: prefer

    ## sets pgbouncer config: `client_tls_ciphers`
    ##
    ciphers: normal

    ## sets pgbouncer config: `client_tls_ca_file`
    ##
    caFile:
      existingSecret: ""
      existingSecretKey: root.crt

    ## sets pgbouncer config: `client_tls_key_file`
    ## - [WARNING] a self-signed cert & key are generated if left empty
    ##
    keyFile:
      existingSecret: ""
      existingSecretKey: client.key

    ## sets pgbouncer config: `client_tls_cert_file`
    ## - [WARNING] a self-signed cert & key are generated if left empty
    ##
    certFile:
      existingSecret: ""
      existingSecretKey: client.crt

  ## ssl configs for: pgbouncer -> postgres
  ##
  serverSSL:
    ## sets pgbouncer config: `server_tls_sslmode`
    ##
    mode: prefer

    ## sets pgbouncer config: `server_tls_ciphers`
    ##
    ciphers: normal

    ## sets pgbouncer config: `server_tls_ca_file`
    ##
    caFile:
      existingSecret: ""
      existingSecretKey: root.crt

    ## sets pgbouncer config: `server_tls_key_file`
    ##
    keyFile:
      existingSecret: ""
      existingSecretKey: server.key

    ## sets pgbouncer config: `server_tls_cert_file`
    ##
    certFile:
      existingSecret: ""
      existingSecretKey: server.crt

###################################
## DATABASE | Embedded Postgres
###################################
postgresql:
  ## if the `stable/postgresql` chart is used
  ## - [WARNING] the embedded Postgres is NOT SUITABLE for production deployments of Airflow
  ## - [WARNING] consider using an external database with `externalDatabase.*`
  ## - set to `false` if using `externalDatabase.*`
  ##
  enabled: true

  ## configs for the postgres container image
  ##
  image:
    registry: ghcr.io
    repository: airflow-helm/postgresql-bitnami
    tag: 11.16-patch.0
    pullPolicy: Always

  ## the postgres database to use
  ##
  postgresqlDatabase: airflow

  ## the postgres user to create
  ##
  postgresqlUsername: postgres

  ## the postgres user's password
  ##
  postgresqlPassword: airflow

  ## the name of a pre-created secret containing the postgres password
  ##
  existingSecret: ""

  ## the key within `postgresql.existingSecret` containing the password string
  ##
  existingSecretKey: "postgresql-password"

  ## configs for the PVC of postgresql
  ##
  persistence:
    ## if postgres will use Persistent Volume Claims to store data
    ## - [WARNING] if false, data will be LOST as postgres Pods restart
    ##
    enabled: true

    ## the name of the StorageClass used by the PVC
    ##
    storageClass: ""

    ## the access modes of the PVC
    ##
    accessModes:
      - ReadWriteOnce

    ## the size of PVC to request
    ##
    size: 8Gi

  ## configs for the postgres StatefulSet
  ##
  master:
    ## the nodeSelector configs for the postgres Pods
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the postgres Pods
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the postgres Pods
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## annotations for the postgres Pods
    ##
    podAnnotations:
      cluster-autoscaler.kubernetes.io/safe-to-evict: "true"

###################################
## DATABASE | External Database
###################################
externalDatabase:
  ## the type of external database
  ## - allowed values: "mysql", "postgres"
  ##
  type: postgres

  ## the host of the external database
  ##
  host: localhost

  ## the port of the external database
  ##
  port: 5432

  ## the database/scheme to use within the external database
  ##
  database: airflow

  ## the username for the external database
  ##
  user: airflow

  ## the name of a pre-created secret containing the external database user
  ## - if set, this overrides `externalDatabase.user`
  ##
  userSecret: ""

  ## the key within `externalDatabase.userSecret` containing the user string
  ##
  userSecretKey: "postgresql-user"

  ## the password for the external database
  ## - [WARNING] to avoid storing the password in plain-text within your values,
  ##   create a Kubernetes secret and use `externalDatabase.passwordSecret`
  ##
  password: ""

  ## the name of a pre-created secret containing the external database password
  ## - if set, this overrides `externalDatabase.password`
  ##
  passwordSecret: ""

  ## the key within `externalDatabase.passwordSecret` containing the password string
  ##
  passwordSecretKey: "postgresql-password"

  ## extra connection-string properties for the external database
  ##
  ## ____ EXAMPLE _______________
  ##   # require SSL (only for Postgres)
  ##   properties: "?sslmode=require"
  ##
  properties: ""

###################################
## DATABASE | Embedded Redis
###################################
redis:
  ## if the `stable/redis` chart is used
  ## - set to `false` if `airflow.executor` is `KubernetesExecutor`
  ## - set to `false` if using `externalRedis.*`
  ##
  enabled: true

  ## configs for the redis container image
  ##
  image:
    registry: docker.io
    repository: bitnami/redis
    tag: 5.0.14-debian-10-r173
    pullPolicy: Always

  ## the redis password
  ##
  password: airflow

  ## the name of a pre-created secret containing the redis password
  ##
  existingSecret: ""

  ## the key within `redis.existingSecret` containing the password string
  ##
  existingSecretPasswordKey: "redis-password"

  ## configs for redis cluster mode
  ##
  cluster:
    ## if redis runs in cluster mode
    ##
    enabled: false

    ## the number of redis slaves
    ##
    slaveCount: 1

  ## configs for the redis master StatefulSet
  ##
  master:
    ## resource requests/limits for the redis master Pods
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the nodeSelector configs for the redis master Pods
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the redis master Pods
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the redis master Pods
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## annotations for the redis master Pods
    ##
    podAnnotations:
      cluster-autoscaler.kubernetes.io/safe-to-evict: "true"

    ## configs for the PVC of the redis master Pods
    ##
    persistence:
      ## use a PVC to persist data
      ##
      enabled: false

      ## the name of the StorageClass used by the PVC
      ##
      storageClass: ""

      ## the access mode of the PVC
      ##
      accessModes:
      - ReadWriteOnce

      ## the size of PVC to request
      ##
      size: 8Gi

  ## configs for the redis slave StatefulSet
  ## - only used if `redis.cluster.enabled` is `true`
  ##
  slave:
    ## resource requests/limits for the slave Pods
    ## - spec for ResourceRequirements:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#resourcerequirements-v1-core
    ##
    resources: {}

    ## the nodeSelector configs for the redis slave Pods
    ## - docs for nodeSelector:
    ##   https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector
    ##
    nodeSelector: {}

    ## the affinity configs for the redis slave Pods
    ## - spec for Affinity:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#affinity-v1-core
    ##
    affinity: {}

    ## the toleration configs for the redis slave Pods
    ## - spec for Toleration:
    ##   https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#toleration-v1-core
    ##
    tolerations: []

    ## annotations for the slave Pods
    ##
    podAnnotations:
      cluster-autoscaler.kubernetes.io/safe-to-evict: "true"

    ## configs for the PVC of the redis slave Pods
    ##
    persistence:
      ## use a PVC to persist data
      ##
      enabled: false

      ## the name of the StorageClass used by the PVC
      ##
      storageClass: ""

      ## the access mode of the PVC
      ##
      accessModes:
        - ReadWriteOnce

      ## the size of PVC to request
      ##
      size: 8Gi

###################################
## DATABASE | External Redis
###################################
externalRedis:
  ## the host of the external redis
  ##
  host: localhost

  ## the port of the external redis
  ##
  port: 6379

  ## the database number to use within the external redis
  ##
  databaseNumber: 1

  ## the password for the external redis
  ## - [WARNING] to avoid storing the password in plain-text within your values,
  ##   create a Kubernetes secret and use `externalRedis.passwordSecret`
  ##
  password: ""

  ## the name of a pre-created secret containing the external redis password
  ## - if set, this overrides `externalRedis.password`
  ##
  passwordSecret: ""

  ## the key within `externalRedis.passwordSecret` containing the password string
  ##
  passwordSecretKey: "redis-password"

  ## extra connection-string properties for the external redis
  ##
  ## ____ EXAMPLE _______________
  ##   properties: "?ssl_cert_reqs=CERT_OPTIONAL"
  ##
  properties: ""

###################################
## CONFIG | ServiceMonitor (Prometheus Operator)
###################################
serviceMonitor:
  ## if ServiceMonitor resources should be deployed for airflow webserver
  ## - [WARNING] you will need a metrics exporter in your `airflow.image`, for example:
  ##   https://github.com/epoch8/airflow-exporter
  ## - ServiceMonitor is a resource from prometheus-operator:
  ##   https://github.com/prometheus-operator/prometheus-operator
  ##
  enabled: false

  ## labels for ServiceMonitor, so that Prometheus can select it
  ##
  selector:
    prometheus: kube-prometheus

  ## the ServiceMonitor web endpoint path
  ##
  path: /admin/metrics

  ## the ServiceMonitor web endpoint interval
  ##
  interval: "30s"

###################################
## CONFIG | PrometheusRule (Prometheus Operator)
###################################
prometheusRule:
  ## if PrometheusRule resources should be deployed for airflow webserver
  ## - [WARNING] you will need a metrics exporter in your `airflow.image`, for example:
  ##   https://github.com/epoch8/airflow-exporter
  ## - PrometheusRule is a resource from prometheus-operator:
  ##   https://github.com/prometheus-operator/prometheus-operator
  ##
  enabled: false

  ## labels for PrometheusRule, so that Prometheus can select it
  ##
  additionalLabels: {}

  ## alerting rules for Prometheus
  ## - docs for alerting rules: https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/
  ##
  groups: []