"""Column specs derived from the microsoft/ARI inventory modules.

GENERATED FILE - do not edit by hand.
Regenerate with:  python tools/generate_ari_configs.py

Source: https://github.com/microsoft/ARI (MIT License, Copyright (c) 2020 RenatoGregio).
Property paths are case-corrected against live Azure Resource Graph data,
because KQL - unlike PowerShell - is case-sensitive on dynamic fields.
"""

from __future__ import annotations

ARI_SPECS: list[dict] = [
 {
  "type": "microsoft.advisor/advisorscore",
  "sheet": "AdvisorScore",
  "module": "APIs/AdvisorScore.ps1",
  "columns": [
   [
    "Latest Refresh Score",
    "tostring(properties['lastrefreshedscore']['date'])"
   ],
   [
    "Latest Score (%)",
    "tostring(properties['lastrefreshedscore']['score'])"
   ]
  ],
  "explode": [
   "properties.timeseries",
   [
    [
     "Consumption Units",
     "consumptionunits",
     "sem_amostra"
    ],
    [
     "Impacted Resources",
     "impactedresourcecount",
     "sem_amostra"
    ],
    [
     "Potential Score Increase",
     "potentialscoreincrease",
     "sem_amostra"
    ],
    [
     "Score",
     "score",
     "sem_amostra"
    ],
    [
     "Score Date",
     "date",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.apimanagement/service",
  "sheet": "APIM",
  "module": "Integration/APIM.ps1",
  "columns": [
   [
    "Backend SSL 3.0",
    "tostring(properties['customProperties'])"
   ],
   [
    "Gateway URL",
    "tostring(properties['gatewayUrl'])"
   ],
   [
    "Public IP",
    "tostring(properties['publicIPAddresses'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Sku Capacity",
    "tostring(sku['capacity'])"
   ],
   [
    "Virtual Network Type",
    "tostring(properties['virtualNetworkType'])"
   ]
  ]
 },
 {
  "type": "microsoft.app/containerapps",
  "sheet": "Container App",
  "module": "Container/ContainerApp.ps1",
  "columns": [
   [
    "Container App Environment",
    "tostring(split(tostring(properties['environmentId']), '/')[8])"
   ],
   [
    "Dapr",
    "tostring(properties['configuration']['dapr'])"
   ],
   [
    "Ingress",
    "tostring(properties['configuration']['ingress'])"
   ],
   [
    "Running Status",
    "tostring(properties['runningStatus'])"
   ],
   [
    "Secrets",
    "tostring(properties['configuration']['secrets'])"
   ],
   [
    "Workload Profile",
    "tostring(properties['workloadProfileName'])"
   ]
  ],
  "explode": [
   "properties.template",
   [
    [
     "CPU Cores",
     "containers.resources.cpu",
     "ok"
    ],
    [
     "Container",
     "containers.name",
     "ok"
    ],
    [
     "Container Image",
     "containers.image",
     "ok"
    ],
    [
     "Ephemeral Storage (Gi)",
     "containers.resources.ephemeralStorage",
     "ok"
    ],
    [
     "Memory Size (Gi)",
     "containers.resources.memory",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.app/managedenvironments",
  "sheet": "Container App Env",
  "module": "Container/ContainerAppEnv.ps1",
  "columns": [
   [
    "Dapr version",
    "tostring(properties['daprConfiguration']['version'])"
   ],
   [
    "KEDA version",
    "tostring(properties['kedaConfiguration']['version'])"
   ],
   [
    "Public Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "Static IP",
    "tostring(properties['staticIp'])"
   ],
   [
    "Zone Redundant",
    "tostring(properties['zoneRedundant'])"
   ]
  ]
 },
 {
  "type": "microsoft.automation/automationaccounts",
  "sheet": "AutomationAccounts",
  "module": "Management/AutomationAccounts.ps1",
  "columns": [
   [
    "Last Modified Time",
    "tostring(properties['lastModifiedTime'])"
   ],
   [
    "Runbook State",
    "tostring(properties['state'])"
   ]
  ]
 },
 {
  "type": "microsoft.automation/automationaccounts/runbooks",
  "sheet": "AutomationAccounts",
  "module": "Management/AutomationAccounts.ps1",
  "columns": [
   [
    "Last Modified Time",
    "tostring(properties['lastModifiedTime'])"
   ],
   [
    "Runbook Description",
    "tostring(properties['description'])"
   ],
   [
    "Runbook State",
    "tostring(properties['state'])"
   ],
   [
    "Runbook Type",
    "tostring(properties['runbookType'])"
   ]
  ]
 },
 {
  "type": "microsoft.avs/privateclouds",
  "sheet": "VMWare",
  "module": "Compute/VMWare.ps1",
  "columns": [
   [
    "Availability Strategy",
    "tostring(properties['availability']['strategy'])"
   ],
   [
    "Cluster Size",
    "tostring(properties['managementcluster']['clustersize'])"
   ],
   [
    "Encryption",
    "tostring(properties['encryption']['status'])"
   ],
   [
    "Express Route Circuit",
    "tostring(split(tostring(properties['circuit']['expressrouteid']), '/')[8])"
   ],
   [
    "External Cloud Links",
    "tostring(properties['externalcloudlinks']['count'])"
   ],
   [
    "HCX Cloud Manager",
    "tostring(properties['endpoints']['hcxcloudmanager'])"
   ],
   [
    "Identity Sources",
    "tostring(properties['identitysources']['count'])"
   ],
   [
    "Internet",
    "tostring(properties['internet'])"
   ],
   [
    "Management Network",
    "tostring(properties['managementnetwork'])"
   ],
   [
    "NSXT Manager",
    "tostring(properties['endpoints']['nsxtmanager'])"
   ],
   [
    "Network Block",
    "tostring(properties['networkblock'])"
   ],
   [
    "Provisioning Network",
    "tostring(properties['provisioningnetwork'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['name'])"
   ],
   [
    "VCSA",
    "tostring(properties['endpoints']['vcsa'])"
   ],
   [
    "Zone",
    "tostring(properties['availability']['zone'])"
   ],
   [
    "vMotion Network",
    "tostring(properties['vmotionnetwork'])"
   ]
  ]
 },
 {
  "type": "microsoft.cache/redis",
  "sheet": "RedisCache",
  "module": "Database/RedisCache.ps1",
  "columns": [
   [
    "Capacity",
    "tostring(properties['sku']['capacity'])"
   ],
   [
    "Enable Non SSL Port",
    "tostring(properties['enableNonSslPort'])"
   ],
   [
    "FQDN",
    "tostring(properties['hostName'])"
   ],
   [
    "Family",
    "tostring(properties['sku']['family'])"
   ],
   [
    "Max Clients",
    "tostring(properties['redisConfiguration'])"
   ],
   [
    "Port",
    "tostring(properties['port'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SSL Port",
    "tostring(properties['sslPort'])"
   ],
   [
    "Sku",
    "tostring(properties['sku']['name'])"
   ],
   [
    "Version",
    "tostring(properties['redisVersion'])"
   ]
  ],
  "multi": [
   [
    "Private Endpoint",
    "properties.privateEndpointConnections",
    "properties.privateEndpoint.id",
    "split:8"
   ]
  ]
 },
 {
  "type": "microsoft.cache/redisenterprise",
  "sheet": "RedisCache",
  "module": "Database/RedisCache.ps1",
  "columns": [
   [
    "FQDN",
    "tostring(properties['hostName'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ]
  ],
  "multi": [
   [
    "Private Endpoint",
    "properties.privateEndpointConnections",
    "properties.privateEndpoint.id",
    "split:8"
   ]
  ]
 },
 {
  "type": "microsoft.classiccompute/domainnames",
  "sheet": "CloudService",
  "module": "Compute/CloudServices.ps1",
  "columns": [
   [
    "Hostname",
    "tostring(properties['hostname'])"
   ],
   [
    "Label",
    "tostring(properties['label'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ]
  ]
 },
 {
  "type": "microsoft.cognitiveservices/accounts",
  "sheet": "Custom Vision",
  "module": "AI/CustomVision.ps1",
  "columns": [
   [
    "Creation Time",
    "tostring(properties['dateCreated'])"
   ],
   [
    "Custom Domain Name",
    "tostring(properties['customSubDomainName'])"
   ],
   [
    "Endpoint",
    "tostring(properties['endpoint'])"
   ],
   [
    "Is Migrated",
    "tostring(properties['isMigrated'])"
   ],
   [
    "Kind",
    "tostring(kind)"
   ],
   [
    "Network Default Action",
    "tostring(properties['networkAcls']['defaultAction'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ]
  ],
  "multi": [
   [
    "IP Rules",
    "properties.networkAcls.ipRules",
    "",
    "contagem"
   ],
   [
    "Virtual Network Rules",
    "properties.networkAcls.virtualNetworkRules",
    "",
    "contagem"
   ]
  ],
  "explode": [
   "properties.privateEndpointConnections",
   [
    [
     "Private Endpoint",
     "",
     "split:8"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.compute/availabilitysets",
  "sheet": "AvSet",
  "module": "Compute/AvailabilitySets.ps1",
  "columns": [
   [
    "Fault Domains",
    "tostring(properties['platformFaultDomainCount'])"
   ],
   [
    "Update Domains",
    "tostring(properties['platformUpdateDomainCount'])"
   ]
  ],
  "multi": [
   [
    "Orphaned",
    "properties.virtualMachines",
    "id",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.compute/cloudservices",
  "sheet": "CloudService",
  "module": "Compute/CloudServices.ps1",
  "columns": [
   [
    "Hostname",
    "tostring(properties['hostname'])"
   ],
   [
    "Label",
    "tostring(properties['label'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ]
  ]
 },
 {
  "type": "microsoft.compute/disks",
  "sheet": "VMDISK",
  "module": "Compute/VMDisk.ps1",
  "columns": [
   [
    "Associated Resource",
    "tostring(split(tostring(managedBy), '/')[8])"
   ],
   [
    "Connection Type",
    "tostring(properties['networkAccessPolicy'])"
   ],
   [
    "Created Time",
    "tostring(properties['timeCreated'])"
   ],
   [
    "Disk IOPS Read / Write",
    "tostring(properties['diskIOPSReadWrite'])"
   ],
   [
    "Disk MBps Read / Write",
    "tostring(properties['diskMBpsReadWrite'])"
   ],
   [
    "Disk Size",
    "tostring(properties['diskSizeGB'])"
   ],
   [
    "Disk State",
    "tostring(properties['diskState'])"
   ],
   [
    "Encryption",
    "tostring(properties['encryption']['type'])"
   ],
   [
    "Hibernation Supported",
    "tostring(properties['supportsHibernation'])"
   ],
   [
    "HyperV Generation",
    "tostring(properties['hyperVGeneration'])"
   ],
   [
    "OS Type",
    "tostring(properties['osType'])"
   ],
   [
    "Performance Tier",
    "tostring(properties['tier'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SKU",
    "tostring(sku)"
   ],
   [
    "Zone",
    "tostring(zones)"
   ]
  ]
 },
 {
  "type": "microsoft.compute/proximityplacementgroups",
  "sheet": "PPG",
  "module": "Compute/PPG.ps1",
  "columns": [
   [
    "Type",
    "tostring(properties['proximityPlacementGroupType'])"
   ]
  ],
  "multi": [
   [
    "Availability Sets",
    "properties.availabilitySets",
    "id",
    "ok"
   ],
   [
    "Orphaned",
    "properties.virtualMachines",
    "id",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.compute/virtualmachines",
  "sheet": "Virtual Machines",
  "module": "Compute/VirtualMachine.ps1",
  "columns": [
   [
    "Admin Username",
    "tostring(properties['osProfile']['adminUsername'])"
   ],
   [
    "Availability Zone",
    "tostring(zones)"
   ],
   [
    "Creation Time",
    "tostring(properties['timeCreated'])"
   ],
   [
    "Disk Controller Type",
    "tostring(properties['storageProfile']['diskControllerType'])"
   ],
   [
    "Host Name",
    "tostring(properties['osProfile']['computerName'])"
   ],
   [
    "Image Reference",
    "tostring(properties['storageProfile']['imageReference']['publisher'])"
   ],
   [
    "Image Version",
    "tostring(properties['storageProfile']['imageReference']['exactVersion'])"
   ],
   [
    "OS Disk Size (GB)",
    "tostring(properties['storageProfile']['osDisk']['diskSizeGB'])"
   ],
   [
    "OS Name",
    "tostring(properties['extended']['instanceView']['osName'])"
   ],
   [
    "OS Type",
    "tostring(properties['storageProfile']['osDisk']['osType'])"
   ],
   [
    "OS Version",
    "tostring(properties['extended']['instanceView']['osVersion'])"
   ],
   [
    "Power State",
    "tostring(properties['extended']['instanceView']['powerState']['displayStatus'])"
   ],
   [
    "VM Size",
    "tostring(properties['hardwareProfile']['vmSize'])"
   ],
   [
    "VM generation",
    "tostring(properties['extended']['instanceView']['hyperVGeneration'])"
   ]
  ]
 },
 {
  "type": "microsoft.compute/virtualmachinescalesets",
  "sheet": "VMSS",
  "module": "Compute/VirtualMachineScaleSet.ps1",
  "columns": [
   [
    "Admin Username",
    "tostring(properties['virtualMachineProfile']['osProfile']['adminUsername'])"
   ],
   [
    "Created Time",
    "tostring(properties['timeCreated'])"
   ],
   [
    "Diagnostics",
    "tostring(properties['virtualMachineProfile']['diagnosticsProfile'])"
   ],
   [
    "Disk Storage Account Type",
    "tostring(properties['virtualMachineProfile']['storageProfile']['osDisk']['managedDisk']['storageAccountType'])"
   ],
   [
    "Fault Domain",
    "tostring(properties['platformFaultDomainCount'])"
   ],
   [
    "Image Version",
    "tostring(properties['virtualMachineProfile']['storageProfile']['imageReference']['sku'])"
   ],
   [
    "Instances",
    "tostring(sku['capacity'])"
   ],
   [
    "OS Image",
    "tostring(properties['virtualMachineProfile']['storageProfile']['imageReference']['offer'])"
   ],
   [
    "SKU Tier",
    "tostring(sku['tier'])"
   ],
   [
    "Upgrade Policy",
    "tostring(properties['upgradePolicy']['mode'])"
   ],
   [
    "VM Name Prefix",
    "tostring(properties['virtualMachineProfile']['osProfile']['computerNamePrefix'])"
   ],
   [
    "VM OS",
    "tostring(properties['virtualMachineProfile']['storageProfile']['osDisk']['osType'])"
   ],
   [
    "VM OS Disk Size (GB)",
    "tostring(properties['virtualMachineProfile']['storageProfile']['osDisk']['diskSizeGB'])"
   ],
   [
    "VM Size",
    "tostring(sku['name'])"
   ]
  ],
  "multi": [
   [
    "Accelerated Networking Enabled",
    "properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations",
    "properties.enableAcceleratedNetworking",
    "ok"
   ],
   [
    "Custom DNS Servers",
    "properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations",
    "properties.dnsSettings.dnsServers",
    "ok"
   ],
   [
    "Network Security Group",
    "properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations",
    "properties.networkSecurityGroup.id",
    "split:8"
   ],
   [
    "Subnet",
    "properties.virtualMachineProfile.networkProfile.networkInterfaceConfigurations",
    "properties.ipConfigurations.properties.subnet.id",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.consumption/reservationrecommendations",
  "sheet": "Reservation Advisor",
  "module": "APIs/ReservationRecom.ps1",
  "columns": [
   [
    "Cost With No Reserved Instance",
    "tostring(properties['costwithnoreservedinstances'])"
   ],
   [
    "Cost With Reserved Instance",
    "tostring(properties['totalcostwithreservedinstances'])"
   ],
   [
    "Current SKU",
    "tostring(sku)"
   ],
   [
    "Instance Flexibility Group",
    "tostring(properties['instanceflexibilitygroup'])"
   ],
   [
    "Instance Flexibility Ratio",
    "tostring(properties['instanceflexibilityratio'])"
   ],
   [
    "Net Savings",
    "tostring(properties['netsavings'])"
   ],
   [
    "Quantity Normalized",
    "tostring(properties['recommendedquantitynormalized'])"
   ],
   [
    "Recommended Number of Reservations",
    "tostring(properties['recommendedquantity'])"
   ],
   [
    "Recommended Size",
    "tostring(properties['normalizedsize'])"
   ],
   [
    "Reservation Term",
    "tostring(properties['term'])"
   ],
   [
    "Resource Type",
    "tostring(properties['resourcetype'])"
   ],
   [
    "Scope",
    "tostring(properties['scope'])"
   ]
  ]
 },
 {
  "type": "microsoft.containerinstance/containergroups",
  "sheet": "CONTAINER",
  "module": "Container/ContainerGroups.ps1",
  "columns": [
   [
    "IP",
    "tostring(properties['ipAddress']['ip'])"
   ],
   [
    "Instance OS Type",
    "tostring(properties['osType'])"
   ]
  ],
  "explode": [
   "properties.containers",
   [
    [
     "Command",
     "properties.command",
     "ok"
    ],
    [
     "Container Image",
     "properties.image",
     "ok"
    ],
    [
     "Container Name",
     "name",
     "ok"
    ],
    [
     "Container State",
     "properties.instanceView.currentState.state",
     "ok"
    ],
    [
     "Port",
     "properties.ports.port",
     "ok"
    ],
    [
     "Protocol",
     "properties.ports.protocol",
     "ok"
    ],
    [
     "Request CPU",
     "properties.resources.requests.cpu",
     "ok"
    ],
    [
     "Request Memory (GB)",
     "properties.resources.requests.memoryInGB",
     "ok"
    ],
    [
     "Restart Count",
     "properties.instanceView.restartCount",
     "ok"
    ],
    [
     "Start Time",
     "properties.instanceView.currentState.startTime",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.containerregistry/registries",
  "sheet": "REGISTRIES",
  "module": "Container/ContainerRegistries.ps1",
  "columns": [
   [
    "Anonymous Pull Enabled",
    "tostring(properties['anonymousPullEnabled'])"
   ],
   [
    "Created Time",
    "tostring(properties['creationDate'])"
   ],
   [
    "Encryption",
    "tostring(properties['encryption']['status'])"
   ],
   [
    "Private Link",
    "tostring(properties['privateEndpointConnections'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Soft Delete Policy",
    "tostring(properties['policies']['softDeletePolicy']['status'])"
   ],
   [
    "Trust Policy",
    "tostring(properties['policies']['trustPolicy']['status'])"
   ],
   [
    "Zone Redundancy",
    "tostring(properties['zoneRedundancy'])"
   ]
  ]
 },
 {
  "type": "microsoft.containerservice/managedclusters",
  "sheet": "AKS",
  "module": "Container/AKS.ps1",
  "columns": [
   [
    "AAD Enabled",
    "tostring(properties['aadProfile'])"
   ],
   [
    "AKS Pricing Tier",
    "tostring(sku['tier'])"
   ],
   [
    "API Server Address",
    "tostring(properties['fqdn'])"
   ],
   [
    "App Gateway Ingress Controller",
    "tostring(properties['addonProfiles']['ingressApplicationGateway']['config']['applicationGatewayName'])"
   ],
   [
    "Automatic Upgrade Type",
    "tostring(properties['autoUpgradeProfile']['upgradeChannel'])"
   ],
   [
    "Cluster Admin ClusterRoleBinding",
    "tostring(properties['aadProfile']['adminGroupObjectIDs'])"
   ],
   [
    "Cluster Managed Identity",
    "tostring(split(tostring(properties['identityProfile']['kubeletidentity']['resourceId']), '/')[8])"
   ],
   [
    "Cluster Power State",
    "tostring(properties['powerState']['code'])"
   ],
   [
    "Infrastructure Resource Group",
    "tostring(properties['nodeResourceGroup'])"
   ],
   [
    "Kubernetes Local Accounts",
    "tostring(properties['disableLocalAccounts'])"
   ],
   [
    "Kubernetes Version",
    "tostring(properties['kubernetesVersion'])"
   ],
   [
    "Network Policy",
    "tostring(properties['networkProfile']['networkPolicy'])"
   ],
   [
    "Network Type (Plugin)",
    "tostring(properties['networkProfile']['networkPlugin'])"
   ],
   [
    "Node Security Channel Type",
    "tostring(properties['autoUpgradeProfile']['nodeOSUpgradeChannel'])"
   ],
   [
    "Outbound Type",
    "tostring(properties['networkProfile']['outboundType'])"
   ],
   [
    "Plugin Mode",
    "tostring(properties['networkProfile']['networkPluginMode'])"
   ],
   [
    "Pod CIDR",
    "tostring(properties['networkProfile']['podCidr'])"
   ],
   [
    "Private Cluster",
    "tostring(properties['apiServerAccessProfile']['enablePrivateCluster'])"
   ],
   [
    "Private Cluster FQDN",
    "tostring(properties['privateFQDN'])"
   ],
   [
    "Role-Based Access Control",
    "tostring(properties['enableRBAC'])"
   ]
  ],
  "explode": [
   "properties.agentPoolProfiles",
   [
    [
     "Autoscale",
     "enableAutoScaling",
     "ok"
    ],
    [
     "Autoscale Maximum Node Count",
     "maxCount",
     "ok"
    ],
    [
     "Autoscale Minimum Node Count",
     "minCount",
     "ok"
    ],
    [
     "Availability Zones",
     "availabilityZones",
     "ok"
    ],
    [
     "Enable Node Public IP",
     "enableNodePublicIP",
     "ok"
    ],
    [
     "Labels",
     "nodeLabels",
     "ok"
    ],
    [
     "Max Pods Per Node",
     "maxPods",
     "ok"
    ],
    [
     "Node Pool Image",
     "nodeImageVersion",
     "ok"
    ],
    [
     "Node Pool Mode",
     "mode",
     "ok"
    ],
    [
     "Node Pool Name",
     "name",
     "ok"
    ],
    [
     "Node Pool OS",
     "osSKU",
     "ok"
    ],
    [
     "Node Pool OS Type",
     "osType",
     "ok"
    ],
    [
     "Node Pool Power State",
     "powerState.code",
     "ok"
    ],
    [
     "Node Pool Size",
     "vmSize",
     "ok"
    ],
    [
     "Node Pool Version",
     "orchestratorVersion",
     "ok"
    ],
    [
     "OS Disk Size (GB)",
     "osDiskSizeGB",
     "ok"
    ],
    [
     "Subnet",
     "vnetSubnetID",
     "split:10"
    ],
    [
     "Taints",
     "nodeTaints",
     "ok"
    ],
    [
     "Target Nodes",
     "count",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.databricks/workspaces",
  "sheet": "Databricks",
  "module": "Analytics/Databricks.ps1",
  "columns": [
   [
    "Created Time",
    "tostring(properties['createdDateTime'])"
   ],
   [
    "Custom Private Subnet",
    "tostring(properties['parameters']['customPrivateSubnetName']['value'])"
   ],
   [
    "Custom Public Subnet",
    "tostring(properties['parameters']['customPublicSubnetName']['value'])"
   ],
   [
    "Custom Virtual Network",
    "tostring(split(tostring(properties['parameters']['customVirtualNetworkId']['value']), '/')[8])"
   ],
   [
    "Enable Public IP",
    "tostring(properties['parameters']['enableNoPublicIp']['value'])"
   ],
   [
    "Infrastructure Encryption",
    "tostring(properties['parameters']['requireInfrastructureEncryption']['value'])"
   ],
   [
    "Managed Resource Group",
    "tostring(split(tostring(properties['managedResourceGroupId']), '/')[4])"
   ],
   [
    "Prepare Encryption",
    "tostring(properties['parameters']['prepareEncryption']['value'])"
   ],
   [
    "Pricing Tier",
    "tostring(sku)"
   ],
   [
    "Storage Account",
    "tostring(properties['parameters']['storageAccountName']['value'])"
   ],
   [
    "Storage Account SKU",
    "tostring(properties['parameters']['storageAccountSkuName']['value'])"
   ],
   [
    "URL",
    "tostring(properties['workspaceUrl'])"
   ]
  ]
 },
 {
  "type": "microsoft.dbformariadb/servers",
  "sheet": "MariaDB",
  "module": "Database/MariaDB.ps1",
  "columns": [
   [
    "Admin Login",
    "tostring(properties['administratorlogin'])"
   ],
   [
    "Auto Grow",
    "tostring(properties['storageprofile']['storageautogrow'])"
   ],
   [
    "BYOK Enforcement",
    "tostring(properties['byokenforcement'])"
   ],
   [
    "Backup Retention Days",
    "tostring(properties['storageprofile']['backupretentiondays'])"
   ],
   [
    "Capacity",
    "tostring(sku)"
   ],
   [
    "Geo-Redundant Backup",
    "tostring(properties['storageprofile']['georedundantbackup'])"
   ],
   [
    "Infrastructure Encryption",
    "tostring(properties['infrastructureencryption'])"
   ],
   [
    "MariaDB Version",
    "tostring(properties['version'])"
   ],
   [
    "Minimum TLS Version",
    "tostring(properties['minimaltlsversion'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicnetworkaccess'])"
   ],
   [
    "Replica Capacity",
    "tostring(properties['replicacapacity'])"
   ],
   [
    "Replication Role",
    "tostring(properties['replicationrole'])"
   ],
   [
    "SSL Enforcement",
    "tostring(properties['sslenforcement'])"
   ],
   [
    "State",
    "tostring(properties['uservisiblestate'])"
   ],
   [
    "Storage MB",
    "tostring(properties['storageprofile']['storagemb'])"
   ]
  ]
 },
 {
  "type": "microsoft.dbformysql/flexibleservers",
  "sheet": "MySQL flexible",
  "module": "Database/MySQLflexible.ps1",
  "columns": [
   [
    "Administrator Login",
    "tostring(properties['administratorLogin'])"
   ],
   [
    "Auto Grow",
    "tostring(properties['storage']['autoGrow'])"
   ],
   [
    "Backup Retention Days",
    "tostring(properties['backup']['backupRetentionDays'])"
   ],
   [
    "Custom Maintenance Window",
    "tostring(properties['maintenanceWindow']['customWindow'])"
   ],
   [
    "FQDN",
    "tostring(properties['fullyQualifiedDomainName'])"
   ],
   [
    "Geo Redundant Backup",
    "tostring(properties['backup']['geoRedundantBackup'])"
   ],
   [
    "High Availability",
    "tostring(properties['highAvailability']['mode'])"
   ],
   [
    "High Availability State",
    "tostring(properties['highAvailability']['state'])"
   ],
   [
    "Limit IOPs",
    "tostring(properties['storage']['iops'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['network']['publicNetworkAccess'])"
   ],
   [
    "Replica Capacity",
    "tostring(properties['replicaCapacity'])"
   ],
   [
    "Replication Role",
    "tostring(properties['replicationRole'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ],
   [
    "Storage Size (GB)",
    "tostring(properties['storage']['storageSizeGB'])"
   ],
   [
    "Storage Sku",
    "tostring(properties['storage']['storageSku'])"
   ],
   [
    "Version",
    "tostring(properties['version'])"
   ],
   [
    "Zone",
    "tostring(properties['availabilityZone'])"
   ]
  ]
 },
 {
  "type": "microsoft.dbformysql/servers",
  "sheet": "MySQL",
  "module": "Database/MySQL.ps1",
  "columns": [
   [
    "Admin Login",
    "tostring(properties['administratorlogin'])"
   ],
   [
    "Auto Grow",
    "tostring(properties['storageprofile']['storageautogrow'])"
   ],
   [
    "BYOK Enforcement",
    "tostring(properties['byokenforcement'])"
   ],
   [
    "Backup Retention Days",
    "tostring(properties['storageprofile']['backupretentiondays'])"
   ],
   [
    "Capacity",
    "tostring(sku)"
   ],
   [
    "Geo-Redundant Backup",
    "tostring(properties['storageprofile']['georedundantbackup'])"
   ],
   [
    "Infrastructure Encryption",
    "tostring(properties['infrastructureencryption'])"
   ],
   [
    "Minimum TLS Version",
    "tostring(properties['minimaltlsversion'])"
   ],
   [
    "MySQL Version",
    "tostring(properties['version'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicnetworkaccess'])"
   ],
   [
    "Replica Capacity",
    "tostring(properties['replicacapacity'])"
   ],
   [
    "Replication Role",
    "tostring(properties['replicationrole'])"
   ],
   [
    "SSL Enforcement",
    "tostring(properties['sslenforcement'])"
   ],
   [
    "State",
    "tostring(properties['uservisiblestate'])"
   ],
   [
    "Storage MB",
    "tostring(properties['storageprofile']['storagemb'])"
   ]
  ]
 },
 {
  "type": "microsoft.dbforpostgresql/flexibleservers",
  "sheet": "POSTGRE Flexible",
  "module": "Database/POSTGREFlexible.ps1",
  "columns": [
   [
    "AD Authentication",
    "tostring(properties['authConfig']['activeDirectoryAuth'])"
   ],
   [
    "ADMIN Login",
    "tostring(properties['administratorLogin'])"
   ],
   [
    "Availability Zone",
    "tostring(properties['availabilityZone'])"
   ],
   [
    "Backup Retention (Days)",
    "tostring(properties['backup']['backupRetentionDays'])"
   ],
   [
    "Computer Size",
    "tostring(sku)"
   ],
   [
    "Data Encryption",
    "tostring(properties['dataEncryption']['type'])"
   ],
   [
    "Delegated Subnet",
    "tostring(split(tostring(properties['network']['delegatedSubnetResourceId']), '/')[10])"
   ],
   [
    "FQDN",
    "tostring(properties['fullyQualifiedDomainName'])"
   ],
   [
    "Geo-Redundant Backup",
    "tostring(properties['backup']['geoRedundantBackup'])"
   ],
   [
    "High Availability",
    "tostring(properties['highAvailability']['state'])"
   ],
   [
    "Password Authentication",
    "tostring(properties['authConfig']['passwordAuth'])"
   ],
   [
    "Private DNS Zone",
    "tostring(split(tostring(properties['network']['privateDnsZoneArmResourceId']), '/')[8])"
   ],
   [
    "Public Network Access",
    "tostring(properties['network']['publicNetworkAccess'])"
   ],
   [
    "Replication Capacity",
    "tostring(properties['replicaCapacity'])"
   ],
   [
    "Replication Role",
    "tostring(properties['replicationRole'])"
   ],
   [
    "Storage Size (GB)",
    "tostring(properties['storage']['storageSizeGB'])"
   ],
   [
    "Version",
    "tostring(properties['minorVersion'])"
   ]
  ]
 },
 {
  "type": "microsoft.dbforpostgresql/servers",
  "sheet": "POSTGRE",
  "module": "Database/POSTGRE.ps1",
  "columns": [
   [
    "Admin Login",
    "tostring(properties['administratorlogin'])"
   ],
   [
    "Auto Grow",
    "tostring(properties['storageprofile']['storageautogrow'])"
   ],
   [
    "BYOK Enforcement",
    "tostring(properties['byokenforcement'])"
   ],
   [
    "Backup Retention Days",
    "tostring(properties['storageprofile']['backupretentiondays'])"
   ],
   [
    "Capacity",
    "tostring(sku)"
   ],
   [
    "Geo-Redundant Backup",
    "tostring(properties['storageprofile']['georedundantbackup'])"
   ],
   [
    "Infrastructure Encryption",
    "tostring(properties['infrastructureencryption'])"
   ],
   [
    "Minimum TLS Version",
    "tostring(properties['minimaltlsversion'])"
   ],
   [
    "Postgre Version",
    "tostring(properties['version'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicnetworkaccess'])"
   ],
   [
    "Replica Capacity",
    "tostring(properties['replicacapacity'])"
   ],
   [
    "Replication Role",
    "tostring(properties['replicationrole'])"
   ],
   [
    "SSL Enforcement",
    "tostring(properties['sslenforcement'])"
   ],
   [
    "State",
    "tostring(properties['uservisiblestate'])"
   ],
   [
    "Storage MB",
    "tostring(properties['storageprofile']['storagemb'])"
   ]
  ]
 },
 {
  "type": "microsoft.desktopvirtualization/hostpools",
  "sheet": "AVD",
  "module": "Compute/AVD.ps1",
  "columns": [
   [
    "HostPool Type",
    "tostring(properties['hostPoolType'])"
   ],
   [
    "LoadBalancer",
    "tostring(properties['loadBalancerType'])"
   ],
   [
    "maxSessionLimit",
    "tostring(properties['maxSessionLimit'])"
   ],
   [
    "preferred AppGroup",
    "tostring(properties['preferredAppGroupType'])"
   ]
  ]
 },
 {
  "type": "microsoft.desktopvirtualization/hostpools/sessionhosts",
  "sheet": "AVD",
  "module": "Compute/AVD.ps1",
  "columns": [
   [
    "HostPool Type",
    "tostring(properties['hostpooltype'])"
   ],
   [
    "LoadBalancer",
    "tostring(properties['loadbalancertype'])"
   ],
   [
    "maxSessionLimit",
    "tostring(properties['maxsessionlimit'])"
   ],
   [
    "preferred AppGroup",
    "tostring(properties['preferredappgrouptype'])"
   ]
  ]
 },
 {
  "type": "microsoft.devices/iothubs",
  "sheet": "IOTHubs",
  "module": "IoT/IOTHubs.ps1",
  "columns": [
   [
    "Event Partition Count",
    "tostring(properties['eventhubendpoints']['events']['partitioncount'])"
   ],
   [
    "Event Retention Time In Days",
    "tostring(properties['eventhubendpoints']['events']['retentiontimeindays'])"
   ],
   [
    "Events Path",
    "tostring(properties['eventhubendpoints']['events']['path'])"
   ],
   [
    "Host Name",
    "tostring(properties['hostname'])"
   ],
   [
    "IP Filter Rules",
    "tostring(properties['ipfilterrules']['count'])"
   ],
   [
    "Max Delivery Count",
    "tostring(properties['cloudtodevice']['maxdeliverycount'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['name'])"
   ],
   [
    "SKU Tier",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ]
  ],
  "explode": [
   "properties.locations",
   [
    [
     "Role",
     "role",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.documentdb/databaseaccounts",
  "sheet": "CosmosDB",
  "module": "Database/CosmosDB.ps1",
  "columns": [
   [
    "Account Offer Type",
    "tostring(properties['databaseAccountOfferType'])"
   ],
   [
    "Backup Policy",
    "tostring(properties['backupPolicy']['type'])"
   ],
   [
    "Backup Storage Redundancy",
    "tostring(properties['backupPolicy']['periodicModeProperties']['backupStorageRedundancy'])"
   ],
   [
    "CORS",
    "tostring(properties['cors'])"
   ],
   [
    "Capabilities",
    "tostring(properties['capabilities'])"
   ],
   [
    "Default Consistency",
    "tostring(properties['consistencyPolicy']['defaultConsistencyLevel'])"
   ],
   [
    "Enabled API Types",
    "tostring(properties['EnabledApiTypes'])"
   ],
   [
    "Free Tier Discount",
    "tostring(properties['enableFreeTier'])"
   ],
   [
    "Public Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "URI",
    "tostring(properties['documentEndpoint'])"
   ],
   [
    "VNET Filtering",
    "tostring(properties['isVirtualNetworkFilterEnabled'])"
   ]
  ],
  "multi": [
   [
    "Read Locations",
    "properties.readLocations",
    "locationName",
    "ok"
   ],
   [
    "Replicate Data Globally",
    "properties.failoverPolicies",
    "",
    "contagem"
   ],
   [
    "Write Locations",
    "properties.writeLocations",
    "locationName",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.eventhub/namespaces",
  "sheet": "EvHub",
  "module": "Analytics/EvtHub.ps1",
  "columns": [
   [
    "Auto-Inflate",
    "tostring(properties['isAutoInflateEnabled'])"
   ],
   [
    "Created Time",
    "tostring(properties['createdAt'])"
   ],
   [
    "Endpoint",
    "tostring(properties['serviceBusEndpoint'])"
   ],
   [
    "Geo-Replication",
    "tostring(properties['zoneRedundant'])"
   ],
   [
    "Kafka Enabled",
    "tostring(properties['kafkaEnabled'])"
   ],
   [
    "Local Authentication",
    "tostring(properties['disableLocalAuth'])"
   ],
   [
    "Max Throughput Units",
    "tostring(properties['maximumThroughputUnits'])"
   ],
   [
    "Minimum TLS Version",
    "tostring(properties['minimumTlsVersion'])"
   ],
   [
    "SKU",
    "tostring(sku)"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Throughput Units",
    "tostring(sku['capacity'])"
   ]
  ]
 },
 {
  "type": "microsoft.hybridcompute/machines",
  "sheet": "EvHub",
  "module": "Hybrid/ARCServers.ps1",
  "columns": [
   [
    "AD FQDN",
    "tostring(properties['adFqdn'])"
   ],
   [
    "Agent Version",
    "tostring(properties['agentVersion'])"
   ],
   [
    "Asset Tag",
    "tostring(properties['detectedProperties']['smbiosAssetTag'])"
   ],
   [
    "Cloud Provider",
    "tostring(properties['cloudMetadata']['provider'])"
   ],
   [
    "DNS FQDN",
    "tostring(properties['dnsFqdn'])"
   ],
   [
    "Display Name",
    "tostring(properties['displayName'])"
   ],
   [
    "Domain",
    "tostring(properties['domainName'])"
   ],
   [
    "Last Status Change",
    "tostring(properties['lastStatusChange'])"
   ],
   [
    "License Channel",
    "tostring(properties['licenseProfile']['licenseChannel'])"
   ],
   [
    "License Status",
    "tostring(properties['licenseProfile']['licenseStatus'])"
   ],
   [
    "License Type",
    "tostring(properties['licenseProfile']['esuProfile']['serverType'])"
   ],
   [
    "Logical Core Count",
    "tostring(properties['detectedProperties']['logicalCoreCount'])"
   ],
   [
    "MS SQL Server",
    "tostring(properties['mssqlDiscovered'])"
   ],
   [
    "Manufacturer",
    "tostring(properties['detectedProperties']['manufacturer'])"
   ],
   [
    "Memory (GB)",
    "tostring(properties['detectedProperties']['totalPhysicalMemoryInGigabytes'])"
   ],
   [
    "Model",
    "tostring(properties['detectedProperties']['model'])"
   ],
   [
    "OS Install Date",
    "tostring(properties['osInstallDate'])"
   ],
   [
    "OS Name",
    "tostring(properties['osName'])"
   ],
   [
    "OS Version",
    "tostring(properties['osVersion'])"
   ],
   [
    "Operating System",
    "tostring(properties['osSku'])"
   ],
   [
    "Processor",
    "tostring(properties['detectedProperties']['processorNames'])"
   ],
   [
    "Processor Count",
    "tostring(properties['detectedProperties']['processorCount'])"
   ],
   [
    "Serial Number",
    "tostring(properties['detectedProperties']['serialNumber'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ]
  ]
 },
 {
  "type": "microsoft.insights/components",
  "sheet": "AppInsights",
  "module": "Monitoring/AppInsights.ps1",
  "columns": [
   [
    "Application Type",
    "tostring(properties['Application_Type'])"
   ],
   [
    "Created Time",
    "tostring(properties['CreationDate'])"
   ],
   [
    "Data Sampling %",
    "tostring(properties['SamplingPercentage'])"
   ],
   [
    "Flow Type",
    "tostring(properties['Flow_Type'])"
   ],
   [
    "Ingestion Mode",
    "tostring(properties['IngestionMode'])"
   ],
   [
    "Public Access For Ingestion",
    "tostring(properties['publicNetworkAccessForIngestion'])"
   ],
   [
    "Public Access For Query",
    "tostring(properties['publicNetworkAccessForQuery'])"
   ],
   [
    "Request Source",
    "tostring(properties['Request_Source'])"
   ],
   [
    "Retention In Days",
    "tostring(properties['RetentionInDays'])"
   ],
   [
    "Version",
    "tostring(properties['Ver'])"
   ]
  ]
 },
 {
  "type": "microsoft.keyvault/vaults",
  "sheet": "Vault",
  "module": "Security/Vault.ps1",
  "columns": [
   [
    "Enable for Disk Encryption",
    "tostring(properties['enabledForDiskEncryption'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['name'])"
   ],
   [
    "SKU Family",
    "tostring(properties['sku']['family'])"
   ],
   [
    "Soft Delete Retention Days",
    "tostring(properties['softDeleteRetentionInDays'])"
   ],
   [
    "Vault Uri",
    "tostring(properties['vaultUri'])"
   ]
  ],
  "explode": [
   "properties.accessPolicies",
   [
    [
     "Access Policy ObjectID",
     "objectId",
     "ok"
    ],
    [
     "Certificate Permissions",
     "permissions.certificates",
     "ok"
    ],
    [
     "Key Permissions",
     "permissions.keys",
     "ok"
    ],
    [
     "Secret Permissions",
     "permissions.secrets",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.kusto/clusters",
  "sheet": "DataExplorerCluster",
  "module": "Analytics/DataExplorerCluster.ps1",
  "columns": [
   [
    "Compute specifications",
    "tostring(sku)"
   ],
   [
    "Data Ingestion Uri",
    "tostring(properties['dataIngestionUri'])"
   ],
   [
    "Disk Encryption",
    "tostring(properties['enableDiskEncryption'])"
   ],
   [
    "Optimized Autoscale",
    "tostring(properties['optimizedAutoscale']['isEnabled'])"
   ],
   [
    "Optimized Autoscale Max",
    "tostring(properties['optimizedAutoscale']['maximum'])"
   ],
   [
    "Optimized Autoscale Min",
    "tostring(properties['optimizedAutoscale']['minimum'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ],
   [
    "State Reason",
    "tostring(properties['stateReason'])"
   ],
   [
    "Streaming Ingestion",
    "tostring(properties['enableStreamingIngest'])"
   ],
   [
    "URI",
    "tostring(properties['uri'])"
   ]
  ],
  "multi": [
   [
    "Tenants Permissions",
    "properties.trustedExternalTenants",
    "value",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.machinelearningservices/workspaces",
  "sheet": "Machine Learning",
  "module": "AI/MachineLearning.ps1",
  "columns": [
   [
    "Application Insight",
    "tostring(split(tostring(properties['applicationInsights']), '/')[8])"
   ],
   [
    "Container Registry",
    "tostring(split(tostring(properties['containerRegistry']), '/')[8])"
   ],
   [
    "Created Time",
    "tostring(properties['creationTime'])"
   ],
   [
    "Description",
    "tostring(properties['description'])"
   ],
   [
    "Discovery Url",
    "tostring(properties['discoveryUrl'])"
   ],
   [
    "Friendly Name",
    "tostring(properties['friendlyName'])"
   ],
   [
    "HBI Workspace",
    "tostring(properties['hbiWorkspace'])"
   ],
   [
    "Key Vault",
    "tostring(split(tostring(properties['keyVault']), '/')[8])"
   ],
   [
    "ML Flow Tracking Uri",
    "tostring(properties['mlFlowTrackingUri'])"
   ],
   [
    "Private Link Count",
    "tostring(properties['privateLinkCount'])"
   ],
   [
    "SKU",
    "tostring(sku)"
   ],
   [
    "Storage Account",
    "tostring(split(tostring(properties['storageAccount']), '/')[8])"
   ],
   [
    "Storage HNS Enabled",
    "tostring(properties['storageHnsEnabled'])"
   ]
  ]
 },
 {
  "type": "microsoft.managedidentity/userassignedidentities",
  "sheet": "ManagedIdentities",
  "module": "APIs/ManagedIds.ps1",
  "columns": [
   [
    "Client ID",
    "tostring(properties['clientId'])"
   ],
   [
    "Principal ID",
    "tostring(properties['principalId'])"
   ]
  ]
 },
 {
  "type": "microsoft.netapp/netappaccounts/capacitypools/volumes",
  "sheet": "NetApp",
  "module": "Storage/NetApp.ps1",
  "columns": [
   [
    "Cool Access",
    "tostring(properties['coolAccess'])"
   ],
   [
    "LDAP",
    "tostring(properties['ldapEnabled'])"
   ],
   [
    "Max Throughput MiB/s",
    "tostring(properties['throughputMibps'])"
   ],
   [
    "Network Features",
    "tostring(properties['networkFeatures'])"
   ],
   [
    "Protocol",
    "tostring(properties['protocolTypes'])"
   ],
   [
    "Quota (TB)",
    "tostring(properties['usageThreshold'])"
   ],
   [
    "SMB Encryption",
    "tostring(properties['smbEncryption'])"
   ],
   [
    "Security Style",
    "tostring(properties['securityStyle'])"
   ],
   [
    "Service Level",
    "tostring(properties['serviceLevel'])"
   ],
   [
    "Subnet Name",
    "tostring(split(tostring(properties['subnetId']), '/')[10])"
   ],
   [
    "UNIX Permissions",
    "tostring(properties['unixPermissions'])"
   ],
   [
    "VMWare Solution",
    "tostring(properties['avsDataStore'])"
   ]
  ],
  "multi": [
   [
    "Export Policy Count",
    "properties.exportPolicy.rules",
    "",
    "contagem"
   ]
  ]
 },
 {
  "type": "microsoft.network/applicationgateways",
  "sheet": "AppGW",
  "module": "Network_2/ApplicationGateways.ps1",
  "columns": [
   [
    "Current Instances",
    "tostring(properties['sku']['capacity'])"
   ],
   [
    "SKU Name",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "State",
    "tostring(properties['operationalState'])"
   ]
  ],
  "multi": [
   [
    "Backend",
    "properties.backendAddressPools",
    "name",
    "ok"
   ],
   [
    "Backend Pool State",
    "properties.backendAddressPools",
    "properties.backendAddresses",
    "ok"
   ],
   [
    "Frontend",
    "properties.frontendIPConfigurations",
    "name",
    "ok"
   ],
   [
    "Frontend Ports",
    "properties.frontendPorts",
    "properties.port",
    "ok"
   ],
   [
    "Gateways",
    "properties.gatewayIPConfigurations",
    "name",
    "ok"
   ],
   [
    "HTTP Listeners",
    "properties.httpListeners",
    "name",
    "ok"
   ],
   [
    "Request Routing Rules",
    "properties.requestRoutingRules",
    "name",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.network/azurefirewalls",
  "sheet": "AzureFirewall",
  "module": "Network_2/AzureFirewall.ps1",
  "columns": [
   [
    "DNS Proxy",
    "tostring(properties['firewallPolicy']['id'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "Threat Intel Mode",
    "tostring(properties['threatIntelMode'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/bastionhosts",
  "sheet": "BASTION",
  "module": "Network_1/BastionHosts.ps1",
  "columns": [
   [
    "DNS Name",
    "tostring(properties['dnsName'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Scale Units",
    "tostring(properties['scaleUnits'])"
   ]
  ],
  "multi": [
   [
    "Public IP",
    "properties.ipConfigurations",
    "properties.publicIPAddress.id",
    "ok"
   ],
   [
    "Virtual Network",
    "properties.ipConfigurations",
    "properties.subnet.id",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.network/connections",
  "sheet": "Connections",
  "module": "Network_1/Connections.ps1",
  "columns": [
   [
    "Connection Protocol",
    "tostring(properties['connectionProtocol'])"
   ],
   [
    "Routing Weight",
    "tostring(properties['routingWeight'])"
   ],
   [
    "Status",
    "tostring(properties['connectionStatus'])"
   ],
   [
    "Type",
    "tostring(properties['connectionType'])"
   ],
   [
    "connectionMode",
    "tostring(properties['connectionMode'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/dnszones",
  "sheet": "PublicDNS",
  "module": "Network_1/PublicDNS.ps1",
  "columns": [
   [
    "Max Number of Record Sets",
    "tostring(properties['maxNumberOfRecordSets'])"
   ],
   [
    "Name Servers",
    "tostring(properties['nameServers'])"
   ],
   [
    "Number of Record Sets",
    "tostring(properties['numberOfRecordSets'])"
   ],
   [
    "Zone Type",
    "tostring(properties['zoneType'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/expressroutecircuits",
  "sheet": "EvHub",
  "module": "Network_1/ExpressRoute.ps1",
  "columns": [
   [
    "Bandwidth",
    "tostring(properties['serviceProviderProperties']['bandwidthInMbps'])"
   ],
   [
    "Billing Model",
    "tostring(sku)"
   ],
   [
    "Circuit Status",
    "tostring(properties['circuitProvisioningState'])"
   ],
   [
    "GlobalReach Enabled",
    "tostring(properties['globalReachEnabled'])"
   ],
   [
    "Peering Location",
    "tostring(properties['serviceProviderProperties']['peeringLocation'])"
   ],
   [
    "Provider",
    "tostring(properties['serviceProviderProperties']['serviceProviderName'])"
   ],
   [
    "Provider Status",
    "tostring(properties['serviceProviderProvisioningState'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/expressroutegateways",
  "sheet": "VirtualWAN",
  "module": "Network_2/VirtualWAN.ps1",
  "columns": [
   [
    "Allow BranchToBranch Traffic",
    "tostring(properties['allowbranchtobranchtraffic'])"
   ],
   [
    "Allow VnetToVnet Traffic",
    "tostring(properties['allowvnettovnettraffic'])"
   ],
   [
    "Device Vendor",
    "tostring(properties['vpnsites']['id']['properties']['deviceproperties']['devicevendor'])"
   ],
   [
    "Device Vendor IpAddress",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['ipaddress'])"
   ],
   [
    "Disable Vpn Encryption",
    "tostring(properties['disablevpnencryption'])"
   ],
   [
    "Link Provider name",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkprovidername'])"
   ],
   [
    "Link Speed in Mbps",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkspeedinmbps'])"
   ],
   [
    "Virtual Site Name",
    "tostring(properties['vpnsites']['id']['name'])"
   ],
   [
    "Virtual Site Private Address Space",
    "tostring(properties['vpnsites']['id']['properties']['addressspace']['addressprefixes'])"
   ]
  ],
  "explode": [
   "properties.virtualhubs.id",
   [
    [
     "HUB Address Prefix",
     "properties.addressprefix",
     "sem_amostra"
    ],
    [
     "HUB Gateway Preference",
     "properties.preferredroutinggateway",
     "sem_amostra"
    ],
    [
     "HUB Location",
     "location",
     "sem_amostra"
    ],
    [
     "HUB Name",
     "name",
     "sem_amostra"
    ],
    [
     "HUB Router ASN",
     "properties.virtualrouterasn",
     "sem_amostra"
    ],
    [
     "HUB Router IPs",
     "properties.virtualrouterips",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/firewallpolicies",
  "sheet": "AzureFirewall",
  "module": "Network_2/AzureFirewall.ps1",
  "columns": [
   [
    "SKU",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "Threat Intel Mode",
    "tostring(properties['threatIntelMode'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/firewallpolicies/rulecollectiongroups",
  "sheet": "AzureFirewall",
  "module": "Network_2/AzureFirewall.ps1",
  "columns": [
   [
    "DNS Proxy",
    "tostring(properties['firewallpolicy']['id'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "Threat Intel Mode",
    "tostring(properties['threatintelmode'])"
   ]
  ],
  "explode": [
   "properties.firewallpolicy.id",
   [
    [
     "Destination",
     "properties.rulecollections.rules.destinationipgroups",
     "sem_amostra"
    ],
    [
     "Destination Port",
     "properties.rulecollections.rules.destinationports",
     "sem_amostra"
    ],
    [
     "Protocol",
     "properties.rulecollections.rules.ipprotocols",
     "sem_amostra"
    ],
    [
     "Rule Action",
     "properties.rulecollections.action.type",
     "sem_amostra"
    ],
    [
     "Rule Collection",
     "properties.rulecollections.name",
     "sem_amostra"
    ],
    [
     "Rule Collection Group",
     "name",
     "sem_amostra"
    ],
    [
     "Rule Collection Group Priority",
     "properties.priority",
     "sem_amostra"
    ],
    [
     "Rule Name",
     "properties.rulecollections.rules.name",
     "sem_amostra"
    ],
    [
     "Rule Priority",
     "properties.rulecollections.priority",
     "sem_amostra"
    ],
    [
     "Rule Type",
     "properties.rulecollections.rules.ruletype",
     "sem_amostra"
    ],
    [
     "Source",
     "properties.rulecollections.rules.sourceipgroups",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/frontdoors",
  "sheet": "Frontdoor",
  "module": "Network_2/Frontdoor.ps1",
  "columns": [
   [
    "Friendly Name",
    "tostring(properties['friendlyName'])"
   ],
   [
    "State",
    "tostring(properties['enabledState'])"
   ],
   [
    "cName",
    "tostring(properties['cName'])"
   ]
  ],
  "multi": [
   [
    "Backend",
    "properties.backendPools",
    "name",
    "ok"
   ],
   [
    "Frontend",
    "properties.frontendEndpoints",
    "name",
    "ok"
   ],
   [
    "Health Probe",
    "properties.healthProbeSettings",
    "name",
    "ok"
   ],
   [
    "Load Balancing",
    "properties.loadBalancingSettings",
    "name",
    "ok"
   ],
   [
    "Routing Rules",
    "properties.routingRules",
    "name",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.network/ipgroups",
  "sheet": "AzureFirewall",
  "module": "Network_2/AzureFirewall.ps1",
  "columns": [
   [
    "DNS Proxy",
    "tostring(properties['firewallpolicy']['id'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "Threat Intel Mode",
    "tostring(properties['threatintelmode'])"
   ]
  ],
  "explode": [
   "properties.firewallpolicy.id",
   [
    [
     "Destination",
     "properties.rulecollections.rules.destinationipgroups",
     "sem_amostra"
    ],
    [
     "Destination Port",
     "properties.rulecollections.rules.destinationports",
     "sem_amostra"
    ],
    [
     "Protocol",
     "properties.rulecollections.rules.ipprotocols",
     "sem_amostra"
    ],
    [
     "Rule Action",
     "properties.rulecollections.action.type",
     "sem_amostra"
    ],
    [
     "Rule Collection",
     "properties.rulecollections.name",
     "sem_amostra"
    ],
    [
     "Rule Collection Group",
     "name",
     "sem_amostra"
    ],
    [
     "Rule Collection Group Priority",
     "properties.priority",
     "sem_amostra"
    ],
    [
     "Rule Name",
     "properties.rulecollections.rules.name",
     "sem_amostra"
    ],
    [
     "Rule Priority",
     "properties.rulecollections.priority",
     "sem_amostra"
    ],
    [
     "Rule Type",
     "properties.rulecollections.rules.ruletype",
     "sem_amostra"
    ],
    [
     "Source",
     "properties.rulecollections.rules.sourceipgroups",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/loadbalancers",
  "sheet": "LoadBalancer",
  "module": "Network_1/LoadBalancer.ps1",
  "columns": [
   [
    "SKU",
    "tostring(sku['name'])"
   ]
  ],
  "multi": [
   [
    "Backend Count",
    "properties.backendAddressPools",
    "",
    "contagem"
   ],
   [
    "Orphaned",
    "properties.backendAddressPools",
    "id",
    "ok"
   ],
   [
    "Probe Count",
    "properties.probes",
    "",
    "contagem"
   ],
   [
    "Usage",
    "properties.backendAddressPools",
    "properties.loadBalancerBackendAddresses",
    "ok"
   ]
  ],
  "explode": [
   "properties.frontendIPConfigurations",
   [
    [
     "Frontend Name",
     "name",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/natgateways",
  "sheet": "NAT Gateway",
  "module": "Network_1/NATGateway.ps1",
  "columns": [
   [
    "Idle Timeout (Min)",
    "tostring(properties['idleTimeoutInMinutes'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ]
  ],
  "explode": [
   "properties.subnets",
   [
    [
     "Subnet",
     "id",
     "split:8"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/networkinterfaces",
  "sheet": "Network Interface",
  "module": "Network_2/NetworkInterface.ps1",
  "columns": [
   [
    "Accelerated Networking",
    "tostring(properties['enableAcceleratedNetworking'])"
   ],
   [
    "Attached Resource",
    "tostring(split(tostring(properties['virtualMachine']['id']), '/')[8])"
   ],
   [
    "DNS Servers",
    "tostring(properties['dnsSettings']['dnsServers'])"
   ],
   [
    "IP Forwarding",
    "tostring(properties['enableIPForwarding'])"
   ],
   [
    "Internal Domain Suffix",
    "tostring(properties['dnsSettings']['internalDomainNameSuffix'])"
   ],
   [
    "MAC Address",
    "tostring(properties['macAddress'])"
   ],
   [
    "Network Security Group",
    "tostring(split(tostring(properties['networkSecurityGroup']['id']), '/')[8])"
   ]
  ],
  "explode": [
   "properties.ipConfigurations",
   [
    [
     "IP Configurations",
     "name",
     "ok"
    ],
    [
     "Primary",
     "properties.primary",
     "ok"
    ],
    [
     "Private IP",
     "properties.privateIPAddress",
     "ok"
    ],
    [
     "Private IP Method",
     "properties.privateIPAllocationMethod",
     "ok"
    ],
    [
     "Private IP Version",
     "properties.privateIPAddressVersion",
     "ok"
    ],
    [
     "Public IP",
     "properties.publicIPAddress.id",
     "ok"
    ],
    [
     "Subnet",
     "properties.subnet.id",
     "split:10"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/networksecuritygroups",
  "sheet": "NetworkSecuritytGroup",
  "module": "Network_2/NetworkSecurityGroup.ps1",
  "columns": [],
  "explode": [
   "properties.securityRules",
   [
    [
     "Action",
     "properties.access",
     "ok"
    ],
    [
     "Destination",
     "properties.destinationAddressPrefixes",
     "ok"
    ],
    [
     "Destination Port",
     "properties.destinationPortRanges",
     "ok"
    ],
    [
     "Direction",
     "properties.direction",
     "ok"
    ],
    [
     "Priority",
     "properties.priority",
     "ok"
    ],
    [
     "Protocol",
     "properties.protocol",
     "ok"
    ],
    [
     "Security Rules",
     "name",
     "ok"
    ],
    [
     "Source",
     "properties.sourceAddressPrefixes",
     "ok"
    ],
    [
     "Source Port",
     "properties.sourcePortRanges",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/privatednszones",
  "sheet": "PrivateDNS",
  "module": "Network_2/PrivateDNS.ps1",
  "columns": [
   [
    "Network Links with Registration",
    "tostring(properties['numberOfVirtualNetworkLinksWithRegistration'])"
   ],
   [
    "Number of Records",
    "tostring(properties['numberOfRecordSets'])"
   ],
   [
    "Virtual Network Links",
    "tostring(properties['numberOfVirtualNetworkLinks'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/privateendpoints",
  "sheet": "Private Endpoints",
  "module": "Network_2/PrivateEndpoint.ps1",
  "columns": [
   [
    "Subnet",
    "tostring(split(tostring(properties['subnet']['id']), '/')[10])"
   ]
  ],
  "multi": [
   [
    "FQDN",
    "properties.networkInterfaces",
    "id",
    "ok"
   ],
   [
    "Private Link Name",
    "properties.privateLinkServiceConnections",
    "name",
    "ok"
   ],
   [
    "Private Link Resource Type",
    "properties.privateLinkServiceConnections",
    "properties.groupIds",
    "ok"
   ],
   [
    "Private Link Status",
    "properties.privateLinkServiceConnections",
    "properties.privateLinkServiceConnectionState.status",
    "ok"
   ],
   [
    "Private Link Target Resource",
    "properties.privateLinkServiceConnections",
    "properties.privateLinkServiceId",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.network/publicipaddresses",
  "sheet": "PublicIP",
  "module": "Network_2/PublicIP.ps1",
  "columns": [
   [
    "Associated Resource",
    "tostring(split(tostring(properties['ipConfiguration']['id']), '/')[8])"
   ],
   [
    "IP Address",
    "tostring(properties['ipAddress'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Type",
    "tostring(properties['publicIPAllocationMethod'])"
   ],
   [
    "Version",
    "tostring(properties['publicIPAddressVersion'])"
   ],
   [
    "Zones",
    "tostring(zones)"
   ]
  ]
 },
 {
  "type": "microsoft.network/routetables",
  "sheet": "ROUTETABLE",
  "module": "Network_1/RouteTables.ps1",
  "columns": [
   [
    "Disable BGP Route Propagation",
    "tostring(properties['disableBgpRoutePropagation'])"
   ]
  ],
  "multi": [
   [
    "Orphaned",
    "properties.subnets",
    "id",
    "ok"
   ]
  ],
  "explode": [
   "properties.routes",
   [
    [
     "Routes",
     "name",
     "ok"
    ],
    [
     "Routes BGP Override",
     "properties.hasBgpOverride",
     "ok"
    ],
    [
     "Routes Next Hop IP",
     "properties.nextHopIpAddress",
     "ok"
    ],
    [
     "Routes Next Hop Type",
     "properties.nextHopType",
     "ok"
    ],
    [
     "Routes Prefixes",
     "properties.addressPrefix",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/trafficmanagerprofiles",
  "sheet": "TrafficManager",
  "module": "Network_1/TrafficManager.ps1",
  "columns": [
   [
    "DNS name",
    "tostring(properties['dnsConfig']['fqdn'])"
   ],
   [
    "Monitor status",
    "tostring(properties['monitorConfig']['profileMonitorStatus'])"
   ],
   [
    "Routing method",
    "tostring(properties['trafficRoutingMethod'])"
   ],
   [
    "Status",
    "tostring(properties['profileStatus'])"
   ]
  ]
 },
 {
  "type": "microsoft.network/virtualhubs",
  "sheet": "VirtualWAN",
  "module": "Network_2/VirtualWAN.ps1",
  "columns": [
   [
    "Allow BranchToBranch Traffic",
    "tostring(properties['allowbranchtobranchtraffic'])"
   ],
   [
    "Allow VnetToVnet Traffic",
    "tostring(properties['allowvnettovnettraffic'])"
   ],
   [
    "Device Vendor",
    "tostring(properties['vpnsites']['id']['properties']['deviceproperties']['devicevendor'])"
   ],
   [
    "Device Vendor IpAddress",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['ipaddress'])"
   ],
   [
    "Disable Vpn Encryption",
    "tostring(properties['disablevpnencryption'])"
   ],
   [
    "Link Provider name",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkprovidername'])"
   ],
   [
    "Link Speed in Mbps",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkspeedinmbps'])"
   ],
   [
    "Virtual Site Name",
    "tostring(properties['vpnsites']['id']['name'])"
   ],
   [
    "Virtual Site Private Address Space",
    "tostring(properties['vpnsites']['id']['properties']['addressspace']['addressprefixes'])"
   ]
  ],
  "explode": [
   "properties.virtualhubs.id",
   [
    [
     "HUB Address Prefix",
     "properties.addressprefix",
     "sem_amostra"
    ],
    [
     "HUB Gateway Preference",
     "properties.preferredroutinggateway",
     "sem_amostra"
    ],
    [
     "HUB Location",
     "location",
     "sem_amostra"
    ],
    [
     "HUB Name",
     "name",
     "sem_amostra"
    ],
    [
     "HUB Router ASN",
     "properties.virtualrouterasn",
     "sem_amostra"
    ],
    [
     "HUB Router IPs",
     "properties.virtualrouterips",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/virtualnetworkgateways",
  "sheet": "VNETGTW",
  "module": "Network_2/VirtualNetworkGateways.ps1",
  "columns": [
   [
    "Active-active mode",
    "tostring(properties['activeActive'])"
   ],
   [
    "BGP ASN",
    "tostring(properties['bgpSettings']['asn'])"
   ],
   [
    "BGP Peer Weight",
    "tostring(properties['bgpSettings']['peerWeight'])"
   ],
   [
    "BGP Peering Address",
    "tostring(properties['bgpSettings']['bgpPeeringAddress'])"
   ],
   [
    "Enable BGP",
    "tostring(properties['enableBgp'])"
   ],
   [
    "Enable Private Address",
    "tostring(properties['enablePrivateIpAddress'])"
   ],
   [
    "Gateway Generation",
    "tostring(properties['vpnGatewayGeneration'])"
   ],
   [
    "Gateway Type",
    "tostring(properties['gatewayType'])"
   ],
   [
    "Migration Status",
    "tostring(properties['virtualNetworkGatewayMigrationStatus']['state'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['tier'])"
   ],
   [
    "VPN Type",
    "tostring(properties['vpnType'])"
   ]
  ],
  "multi": [
   [
    "Gateway Public IP",
    "properties.ipConfigurations",
    "properties.publicIPAddress.id",
    "split:8"
   ],
   [
    "Gateway Subnet Name",
    "properties.ipConfigurations",
    "properties.subnet.id",
    "split:8"
   ]
  ]
 },
 {
  "type": "microsoft.network/virtualnetworks",
  "sheet": "VirtualNetwork",
  "module": "Network_1/VirtualNetwork.ps1",
  "columns": [
   [
    "Address Space",
    "tostring(properties['addressSpace']['addressPrefixes'])"
   ],
   [
    "DNS Servers",
    "tostring(properties['dhcpOptions']['dnsServers'])"
   ],
   [
    "Enable DDOS Protection",
    "tostring(properties['enableDdosProtection'])"
   ]
  ],
  "explode": [
   "properties.subnets",
   [
    [
     "Consumed IPs",
     "properties.ipConfigurations.id",
     "contagem"
    ],
    [
     "Private Subnet",
     "properties.defaultOutboundAccess",
     "ok"
    ],
    [
     "Subnet Delegations",
     "properties.delegations.properties.serviceName",
     "ok"
    ],
    [
     "Subnet Name",
     "name",
     "ok"
    ],
    [
     "Subnet Network Security Group",
     "properties.networkSecurityGroup.id",
     "ok"
    ],
    [
     "Subnet Prefix",
     "properties.addressPrefix",
     "ok"
    ],
    [
     "Subnet Private Endpoint Network Policies",
     "properties.privateEndpointNetworkPolicies",
     "ok"
    ],
    [
     "Subnet Private Link Service Network Policies",
     "properties.privateLinkServiceNetworkPolicies",
     "ok"
    ],
    [
     "Subnet Route Table",
     "properties.routeTable.id",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/virtualwans",
  "sheet": "VirtualWAN",
  "module": "Network_2/VirtualWAN.ps1",
  "columns": [
   [
    "Allow BranchToBranch Traffic",
    "tostring(properties['allowbranchtobranchtraffic'])"
   ],
   [
    "Allow VnetToVnet Traffic",
    "tostring(properties['allowvnettovnettraffic'])"
   ],
   [
    "Device Vendor",
    "tostring(properties['vpnsites']['id']['properties']['deviceproperties']['devicevendor'])"
   ],
   [
    "Device Vendor IpAddress",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['ipaddress'])"
   ],
   [
    "Disable Vpn Encryption",
    "tostring(properties['disablevpnencryption'])"
   ],
   [
    "Link Provider name",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkprovidername'])"
   ],
   [
    "Link Speed in Mbps",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkspeedinmbps'])"
   ],
   [
    "Virtual Site Name",
    "tostring(properties['vpnsites']['id']['name'])"
   ],
   [
    "Virtual Site Private Address Space",
    "tostring(properties['vpnsites']['id']['properties']['addressspace']['addressprefixes'])"
   ]
  ],
  "explode": [
   "properties.virtualhubs.id",
   [
    [
     "HUB Address Prefix",
     "properties.addressprefix",
     "sem_amostra"
    ],
    [
     "HUB Gateway Preference",
     "properties.preferredroutinggateway",
     "sem_amostra"
    ],
    [
     "HUB Location",
     "location",
     "sem_amostra"
    ],
    [
     "HUB Name",
     "name",
     "sem_amostra"
    ],
    [
     "HUB Router ASN",
     "properties.virtualrouterasn",
     "sem_amostra"
    ],
    [
     "HUB Router IPs",
     "properties.virtualrouterips",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.network/vpnsites",
  "sheet": "VirtualWAN",
  "module": "Network_2/VirtualWAN.ps1",
  "columns": [
   [
    "Allow BranchToBranch Traffic",
    "tostring(properties['allowbranchtobranchtraffic'])"
   ],
   [
    "Allow VnetToVnet Traffic",
    "tostring(properties['allowvnettovnettraffic'])"
   ],
   [
    "Device Vendor",
    "tostring(properties['vpnsites']['id']['properties']['deviceproperties']['devicevendor'])"
   ],
   [
    "Device Vendor IpAddress",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['ipaddress'])"
   ],
   [
    "Disable Vpn Encryption",
    "tostring(properties['disablevpnencryption'])"
   ],
   [
    "Link Provider name",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkprovidername'])"
   ],
   [
    "Link Speed in Mbps",
    "tostring(properties['vpnsites']['id']['properties']['vpnsitelinks']['properties']['linkproperties']['linkspeedinmbps'])"
   ],
   [
    "Virtual Site Name",
    "tostring(properties['vpnsites']['id']['name'])"
   ],
   [
    "Virtual Site Private Address Space",
    "tostring(properties['vpnsites']['id']['properties']['addressspace']['addressprefixes'])"
   ]
  ],
  "explode": [
   "properties.virtualhubs.id",
   [
    [
     "HUB Address Prefix",
     "properties.addressprefix",
     "sem_amostra"
    ],
    [
     "HUB Gateway Preference",
     "properties.preferredroutinggateway",
     "sem_amostra"
    ],
    [
     "HUB Location",
     "location",
     "sem_amostra"
    ],
    [
     "HUB Name",
     "name",
     "sem_amostra"
    ],
    [
     "HUB Router ASN",
     "properties.virtualrouterasn",
     "sem_amostra"
    ],
    [
     "HUB Router IPs",
     "properties.virtualrouterips",
     "sem_amostra"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.operationalinsights/workspaces",
  "sheet": "WrkSpace",
  "module": "Monitoring/Workspaces.ps1",
  "columns": [
   [
    "Created Time",
    "tostring(properties['createdDate'])"
   ],
   [
    "Daily Cap (GB)",
    "tostring(properties['workspaceCapping']['dailyQuotaGb'])"
   ],
   [
    "Data Ingestion From Public Networks",
    "tostring(properties['publicNetworkAccessForIngestion'])"
   ],
   [
    "Queries From Public Networks",
    "tostring(properties['publicNetworkAccessForQuery'])"
   ],
   [
    "Retention Days",
    "tostring(properties['retentionInDays'])"
   ],
   [
    "SKU",
    "tostring(properties['sku']['name'])"
   ]
  ]
 },
 {
  "type": "microsoft.purview/accounts",
  "sheet": "Purview",
  "module": "Analytics/Purview.ps1",
  "columns": [
   [
    "Cloud Connectors",
    "tostring(array_length(properties['cloudConnectors']))"
   ],
   [
    "Created By",
    "tostring(properties['createdBy'])"
   ],
   [
    "Created Time",
    "tostring(properties['createdAt'])"
   ],
   [
    "Friendly Name",
    "tostring(properties['friendlyName'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ]
  ],
  "multi": [
   [
    "Private Endpoints",
    "properties.privateEndpointConnections",
    "",
    "contagem"
   ]
  ]
 },
 {
  "type": "microsoft.recoveryservices/vaults",
  "sheet": "RecoveryVault",
  "module": "Management/RecoveryVault.ps1",
  "columns": [
   [
    "Private Endpoint State for Backup",
    "tostring(properties['privateEndpointStateForBackup'])"
   ],
   [
    "Private Endpoint State for Site Recovery",
    "tostring(properties['privateEndpointStateForSiteRecovery'])"
   ],
   [
    "SKU Name",
    "tostring(sku['name'])"
   ],
   [
    "SKU Tier",
    "tostring(sku['tier'])"
   ]
  ]
 },
 {
  "type": "microsoft.recoveryservices/vaults/backupfabrics/protectioncontainers/protecteditems",
  "sheet": "Backup",
  "module": "Management/Backup.ps1",
  "columns": [
   [
    "Backup Compression",
    "tostring(properties['settings']['iscompression'])"
   ],
   [
    "Datasource Type",
    "tostring(properties['workloadtype'])"
   ],
   [
    "Policy Type",
    "tostring(properties['subprotectionpolicy']['policytype'])"
   ],
   [
    "Protected Items Count",
    "tostring(properties['protecteditemscount'])"
   ],
   [
    "SQL Compression",
    "tostring(properties['settings']['issqlcompression'])"
   ]
  ]
 },
 {
  "type": "microsoft.recoveryservices/vaults/backuppolicies",
  "sheet": "Backup",
  "module": "Management/Backup.ps1",
  "columns": [
   [
    "Backup Compression",
    "tostring(properties['settings']['iscompression'])"
   ],
   [
    "Datasource Type",
    "tostring(properties['workloadtype'])"
   ],
   [
    "Policy Type",
    "tostring(properties['subprotectionpolicy']['policytype'])"
   ],
   [
    "Protected Items Count",
    "tostring(properties['protecteditemscount'])"
   ],
   [
    "SQL Compression",
    "tostring(properties['settings']['issqlcompression'])"
   ]
  ]
 },
 {
  "type": "microsoft.redhatopenshift/openshiftclusters",
  "sheet": "ARO",
  "module": "Container/ARO.ps1",
  "columns": [
   [
    "API Server IP",
    "tostring(properties['apiserverProfile']['ip'])"
   ],
   [
    "API Server URL",
    "tostring(properties['apiserverProfile']['url'])"
   ],
   [
    "API Server type",
    "tostring(properties['apiserverProfile']['visibility'])"
   ],
   [
    "ARO Domain",
    "tostring(properties['clusterProfile']['domain'])"
   ],
   [
    "ARO Version",
    "tostring(properties['clusterProfile']['version'])"
   ],
   [
    "Console URL",
    "tostring(properties['consoleProfile']['url'])"
   ],
   [
    "Docker Pod Cidr",
    "tostring(properties['networkProfile']['podCidr'])"
   ],
   [
    "Master SKU",
    "tostring(properties['masterProfile']['vmSize'])"
   ],
   [
    "Master Subnet",
    "tostring(properties['masterProfile']['subnetId'])"
   ],
   [
    "Service Cidr",
    "tostring(properties['networkProfile']['serviceCidr'])"
   ]
  ],
  "multi": [
   [
    "Ingress Profile IP",
    "properties.ingressProfiles",
    "ip",
    "ok"
   ],
   [
    "Ingress Profile Name",
    "properties.ingressProfiles",
    "name",
    "ok"
   ],
   [
    "Ingress Profile type",
    "properties.ingressProfiles",
    "visibility",
    "ok"
   ],
   [
    "Total Worker Nodes",
    "properties.workerProfiles",
    "count",
    "ok"
   ],
   [
    "Worker DiskSize",
    "properties.workerProfiles",
    "diskSizeGB",
    "ok"
   ],
   [
    "Worker SKU",
    "properties.workerProfiles",
    "vmSize",
    "ok"
   ],
   [
    "Worker Subnet",
    "properties.workerProfiles",
    "subnetId",
    "ok"
   ]
  ]
 },
 {
  "type": "microsoft.resourcehealth/events",
  "sheet": "Outages",
  "module": "APIs/Outages.ps1",
  "columns": [
   [
    "Event Level",
    "tostring(properties['eventlevel'])"
   ],
   [
    "Event Type",
    "tostring(properties['eventtype'])"
   ],
   [
    "Impact Mitigation Time",
    "tostring(properties['impactmitigationtime'])"
   ],
   [
    "Impact Start Time",
    "tostring(properties['impactstarttime'])"
   ],
   [
    "Impacted Services",
    "tostring(properties['impact']['impactedservice'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Title",
    "tostring(properties['title'])"
   ]
  ]
 },
 {
  "type": "microsoft.search/searchservices",
  "sheet": "SearchServices",
  "module": "AI/SearchServices.ps1",
  "columns": [
   [
    "Disable Local Authentication",
    "tostring(properties['disableLocalAuth'])"
   ],
   [
    "Encryption Enforcement",
    "tostring(properties['encryptionWithCmk']['enforcement'])"
   ],
   [
    "Hosting Mode",
    "tostring(properties['hostingMode'])"
   ],
   [
    "Network Rule Set",
    "tostring(properties['networkRuleSet']['bypass'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "Replica Count",
    "tostring(properties['replicaCount'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Semantic Search",
    "tostring(properties['semanticSearch'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Status Details",
    "tostring(properties['statusDetails'])"
   ]
  ],
  "explode": [
   "properties.privateEndpointConnections",
   [
    [
     "Private Endpoint",
     "",
     "split:8"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.servicebus/namespaces",
  "sheet": "ServiceBUS",
  "module": "Integration/ServiceBUS.ps1",
  "columns": [
   [
    "Created Time",
    "tostring(properties['createdAt'])"
   ],
   [
    "Endpoint",
    "tostring(properties['serviceBusEndpoint'])"
   ],
   [
    "Geo-Replication",
    "tostring(properties['zoneRedundant'])"
   ],
   [
    "SKU",
    "tostring(sku)"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Throughput Units",
    "tostring(sku['capacity'])"
   ]
  ]
 },
 {
  "type": "microsoft.servicefabric/clusters",
  "sheet": "VMSS",
  "module": "Compute/VirtualMachineScaleSet.ps1",
  "columns": [
   [
    "Accelerated Networking Enabled",
    "tostring(properties['virtualmachineprofile']['networkprofile']['networkinterfaceconfigurations']['properties']['enableacceleratednetworking'])"
   ],
   [
    "Admin Username",
    "tostring(properties['virtualmachineprofile']['osprofile']['adminusername'])"
   ],
   [
    "Created Time",
    "tostring(properties['timecreated'])"
   ],
   [
    "Custom DNS Servers",
    "tostring(properties['virtualmachineprofile']['networkprofile']['networkinterfaceconfigurations']['properties']['dnssettings']['dnsservers'])"
   ],
   [
    "Diagnostics",
    "tostring(properties['virtualmachineprofile']['diagnosticsprofile'])"
   ],
   [
    "Disk Storage Account Type",
    "tostring(properties['virtualmachineprofile']['storageprofile']['osdisk']['manageddisk']['storageaccounttype'])"
   ],
   [
    "Fault Domain",
    "tostring(properties['platformfaultdomaincount'])"
   ],
   [
    "Image Version",
    "tostring(properties['virtualmachineprofile']['storageprofile']['imagereference']['sku'])"
   ],
   [
    "Instances",
    "tostring(sku['capacity'])"
   ],
   [
    "Network Security Group",
    "tostring(split(tostring(properties['virtualmachineprofile']['networkprofile']['networkinterfaceconfigurations']['properties']['networksecuritygroup']['id']), '/')[8])"
   ],
   [
    "OS Image",
    "tostring(properties['virtualmachineprofile']['storageprofile']['imagereference']['offer'])"
   ],
   [
    "SKU Tier",
    "tostring(sku['tier'])"
   ],
   [
    "Subnet",
    "tostring(properties['virtualmachineprofile']['networkprofile']['networkinterfaceconfigurations']['properties']['ipconfigurations']['properties']['subnet']['id'])"
   ],
   [
    "Upgrade Policy",
    "tostring(properties['upgradepolicy']['mode'])"
   ],
   [
    "VM Name Prefix",
    "tostring(properties['virtualmachineprofile']['osprofile']['computernameprefix'])"
   ],
   [
    "VM OS",
    "tostring(properties['virtualmachineprofile']['storageprofile']['osdisk']['ostype'])"
   ],
   [
    "VM OS Disk Size (GB)",
    "tostring(properties['virtualmachineprofile']['storageprofile']['osdisk']['disksizegb'])"
   ],
   [
    "VM Size",
    "tostring(sku['name'])"
   ]
  ]
 },
 {
  "type": "microsoft.sql/managedinstances",
  "sheet": "SQL MI",
  "module": "Database/SQLMI.ps1",
  "columns": [
   [
    "FQDN",
    "tostring(properties['fullyQualifiedDomainName'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicDataEndpointEnabled'])"
   ],
   [
    "SkuCapacity",
    "tostring(sku['capacity'])"
   ],
   [
    "SkuName",
    "tostring(sku['name'])"
   ],
   [
    "SkuTier",
    "tostring(sku['tier'])"
   ],
   [
    "Zone Redundant",
    "tostring(properties['zoneRedundant'])"
   ],
   [
    "licenseType",
    "tostring(properties['licenseType'])"
   ]
  ]
 },
 {
  "type": "microsoft.sql/managedinstances/databases",
  "sheet": "SQL MI DBs",
  "module": "Database/SQLMIDB.ps1",
  "columns": [
   [
    "Collation",
    "tostring(properties['collation'])"
   ],
   [
    "CreationDate",
    "tostring(properties['creationDate'])"
   ],
   [
    "DefaultSecondaryLocation",
    "tostring(properties['defaultSecondaryLocation'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ]
  ]
 },
 {
  "type": "microsoft.sql/servers",
  "sheet": "SQLSERVER",
  "module": "Database/SQLSERVER.ps1",
  "columns": [
   [
    "Admin Login",
    "tostring(properties['administratorLogin'])"
   ],
   [
    "FQDN",
    "tostring(properties['fullyQualifiedDomainName'])"
   ],
   [
    "Kind",
    "tostring(kind)"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ],
   [
    "Version",
    "tostring(properties['version'])"
   ],
   [
    "minimalTlsVersion",
    "tostring(properties['minimalTlsVersion'])"
   ]
  ],
  "explode": [
   "properties.privateEndpointConnections",
   [
    [
     "Private Endpoint",
     "id",
     "ok"
    ]
   ]
  ]
 },
 {
  "type": "microsoft.sql/servers/databases",
  "sheet": "SQLDB",
  "module": "Database/SQLDB.ps1",
  "columns": [
   [
    "Availability Zone",
    "tostring(properties['availabilityZone'])"
   ],
   [
    "Catalog Collation",
    "tostring(properties['catalogCollation'])"
   ],
   [
    "DTU Capacity",
    "tostring(properties['currentSku']['capacity'])"
   ],
   [
    "Data Max Size (GB)",
    "tostring(properties['maxSizeBytes'])"
   ],
   [
    "Default Secondary Location",
    "tostring(properties['defaultSecondaryLocation'])"
   ],
   [
    "Earliest Restore Point",
    "tostring(properties['earliestRestoreDate'])"
   ],
   [
    "Hardware Configuration",
    "tostring(properties['currentSku']['name'])"
   ],
   [
    "Min DTU Capacity",
    "tostring(properties['minCapacity'])"
   ],
   [
    "Service Tier",
    "tostring(properties['currentSku']['tier'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Zone Redundant",
    "tostring(properties['zoneRedundant'])"
   ]
  ]
 },
 {
  "type": "microsoft.sql/servers/elasticpools",
  "sheet": "SQLPOOL",
  "module": "Database/SQLPOOL.ps1",
  "columns": [
   [
    "Capacity",
    "tostring(sku['capacity'])"
   ],
   [
    "DB Max DTU",
    "tostring(properties['perDatabaseSettings']['maxCapacity'])"
   ],
   [
    "DB Min DTU",
    "tostring(properties['perDatabaseSettings']['minCapacity'])"
   ],
   [
    "Edition",
    "tostring(sku['tier'])"
   ],
   [
    "License",
    "tostring(properties['licenseType'])"
   ],
   [
    "Max Size (GB)",
    "tostring(properties['maxSizeBytes'])"
   ],
   [
    "Sku Name",
    "tostring(sku['name'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ],
   [
    "Zone Redundant",
    "tostring(properties['zoneRedundant'])"
   ]
  ]
 },
 {
  "type": "microsoft.sqlvirtualmachine/sqlvirtualmachines",
  "sheet": "SQLVM",
  "module": "Database/SQLVM.ps1",
  "columns": [
   [
    "SQL Image",
    "tostring(properties['sqlImageOffer'])"
   ],
   [
    "SQL Image Sku",
    "tostring(properties['sqlImageSku'])"
   ],
   [
    "SQL Management",
    "tostring(properties['sqlManagement'])"
   ],
   [
    "SQL Server License Type",
    "tostring(properties['sqlServerLicenseType'])"
   ]
  ]
 },
 {
  "type": "microsoft.storage/storageaccounts",
  "sheet": "StorageAcc",
  "module": "Storage/StorageAccounts.ps1",
  "columns": [
   [
    "Access Tier",
    "tostring(properties['accessTier'])"
   ],
   [
    "Allow Blob Anonymous Access",
    "tostring(properties['allowBlobPublicAccess'])"
   ],
   [
    "Allow Cross Tenant Replication",
    "tostring(properties['allowCrossTenantReplication'])"
   ],
   [
    "Allow Storage Account Key Access",
    "tostring(properties['allowSharedKeyAccess'])"
   ],
   [
    "Created Time",
    "tostring(properties['creationTime'])"
   ],
   [
    "Firewall Exceptions",
    "tostring(properties['networkAcls']['bypass'])"
   ],
   [
    "Hierarchical Namespace",
    "tostring(properties['isHnsEnabled'])"
   ],
   [
    "Infrastructure Encryption Enabled",
    "tostring(properties['encryption']['requireInfrastructureEncryption'])"
   ],
   [
    "Large File Shares",
    "tostring(properties['largeFileSharesState'])"
   ],
   [
    "Minimum TLS Version",
    "tostring(properties['minimumTlsVersion'])"
   ],
   [
    "NFSv3 Enabled",
    "tostring(properties['isNfsV3Enabled'])"
   ],
   [
    "Primary Location",
    "tostring(properties['primaryLocation'])"
   ],
   [
    "SFTP Enabled",
    "tostring(properties['isSftpEnabled'])"
   ],
   [
    "SKU",
    "tostring(sku['name'])"
   ],
   [
    "Secondary Location",
    "tostring(properties['secondaryLocation'])"
   ],
   [
    "Secure Transfer Required",
    "tostring(properties['supportsHttpsTrafficOnly'])"
   ],
   [
    "Status Of Primary Location",
    "tostring(properties['statusOfPrimary'])"
   ],
   [
    "Status Of Secondary Location",
    "tostring(properties['statusOfSecondary'])"
   ],
   [
    "Storage Account Kind",
    "tostring(kind)"
   ],
   [
    "Tier",
    "tostring(sku['tier'])"
   ]
  ]
 },
 {
  "type": "microsoft.streamanalytics/clusters",
  "sheet": "Streamanalytics",
  "module": "Analytics/Streamanalytics.ps1",
  "columns": [
   [
    "Compatibility Level",
    "tostring(properties['compatibilitylevel'])"
   ],
   [
    "Content Storage Policy",
    "tostring(properties['contentstoragepolicy'])"
   ],
   [
    "Created Date",
    "tostring(properties['createddate'])"
   ],
   [
    "Data Locale",
    "tostring(properties['datalocale'])"
   ],
   [
    "Job Pricing Plan",
    "tostring(properties['sku']['name'])"
   ],
   [
    "Job State",
    "tostring(properties['jobstate'])"
   ],
   [
    "Job Type",
    "tostring(properties['jobtype'])"
   ],
   [
    "Last Output Event Time",
    "tostring(properties['lastoutputeventtime'])"
   ],
   [
    "Late Arrival Max Delay in Seconds",
    "tostring(properties['eventslatearrivalmaxdelayinseconds'])"
   ],
   [
    "Out of Order Max Delay in Seconds",
    "tostring(properties['eventsoutofordermaxdelayinseconds'])"
   ],
   [
    "Out of Order Policy",
    "tostring(properties['eventsoutoforderpolicy'])"
   ],
   [
    "Output Error Policy",
    "tostring(properties['outputerrorpolicy'])"
   ],
   [
    "Output Start Time",
    "tostring(properties['outputstarttime'])"
   ],
   [
    "Storage Account",
    "tostring(properties['jobstorageaccount']['accountname'])"
   ],
   [
    "Storage Account Auth Method",
    "tostring(properties['jobstorageaccount']['authenticationmode'])"
   ]
  ]
 },
 {
  "type": "microsoft.streamanalytics/streamingjobs",
  "sheet": "Streamanalytics",
  "module": "Analytics/Streamanalytics.ps1",
  "columns": [
   [
    "Compatibility Level",
    "tostring(properties['compatibilityLevel'])"
   ],
   [
    "Content Storage Policy",
    "tostring(properties['contentStoragePolicy'])"
   ],
   [
    "Created Date",
    "tostring(properties['createdDate'])"
   ],
   [
    "Data Locale",
    "tostring(properties['dataLocale'])"
   ],
   [
    "Job Pricing Plan",
    "tostring(properties['sku']['name'])"
   ],
   [
    "Job State",
    "tostring(properties['jobState'])"
   ],
   [
    "Job Type",
    "tostring(properties['jobType'])"
   ],
   [
    "Last Output Event Time",
    "tostring(properties['lastOutputEventTime'])"
   ],
   [
    "Late Arrival Max Delay in Seconds",
    "tostring(properties['eventsLateArrivalMaxDelayInSeconds'])"
   ],
   [
    "Out of Order Max Delay in Seconds",
    "tostring(properties['eventsOutOfOrderMaxDelayInSeconds'])"
   ],
   [
    "Out of Order Policy",
    "tostring(properties['eventsOutOfOrderPolicy'])"
   ],
   [
    "Output Error Policy",
    "tostring(properties['outputErrorPolicy'])"
   ],
   [
    "Output Start Time",
    "tostring(properties['outputStartTime'])"
   ],
   [
    "Storage Account",
    "tostring(properties['jobStorageAccount']['accountName'])"
   ],
   [
    "Storage Account Auth Method",
    "tostring(properties['jobStorageAccount']['authenticationMode'])"
   ]
  ]
 },
 {
  "type": "microsoft.support/supporttickets",
  "sheet": "SupportTickets",
  "module": "APIs/SupportTickets.ps1",
  "columns": [
   [
    "24/7 Response",
    "tostring(properties['require24x7response'])"
   ],
   [
    "Creation Date",
    "tostring(properties['createddate'])"
   ],
   [
    "Current Severity",
    "tostring(properties['severity'])"
   ],
   [
    "Last Modified Date",
    "tostring(properties['modifieddate'])"
   ],
   [
    "Problem Start Date",
    "tostring(properties['problemstarttime'])"
   ],
   [
    "Service",
    "tostring(properties['servicedisplayname'])"
   ],
   [
    "Status",
    "tostring(properties['status'])"
   ],
   [
    "Support Engineer",
    "tostring(properties['supportengineer']['emailaddress'])"
   ],
   [
    "Support Plan",
    "tostring(properties['supportplantype'])"
   ],
   [
    "Support Ticket",
    "tostring(properties['supportticketid'])"
   ],
   [
    "Ticket Contact Country",
    "tostring(properties['contactdetails']['country'])"
   ],
   [
    "Ticket Contact Email",
    "tostring(properties['contactdetails']['primaryemailaddress'])"
   ],
   [
    "Ticket Contact Name",
    "tostring(properties['contactdetails']['firstname'])"
   ],
   [
    "Ticket SLA (minutes)",
    "tostring(properties['servicelevelagreement']['slaminutes'])"
   ],
   [
    "Title",
    "tostring(properties['title'])"
   ]
  ]
 },
 {
  "type": "microsoft.synapse/workspaces",
  "sheet": "Synapse",
  "module": "Analytics/Synapse.ps1",
  "columns": [
   [
    "Double Encryption Enabled",
    "tostring(properties['encryption']['doubleEncryptionEnabled'])"
   ],
   [
    "Managed ResourceGroup",
    "tostring(properties['managedResourceGroupName'])"
   ],
   [
    "Public Network Access",
    "tostring(properties['publicNetworkAccess'])"
   ],
   [
    "SQL Administrator Login",
    "tostring(properties['sqlAdministratorLogin'])"
   ],
   [
    "Scope Enabled",
    "tostring(properties['extraProperties']['IsScopeEnabled'])"
   ],
   [
    "Trusted Service Bypass Enabled",
    "tostring(properties['trustedServiceBypassEnabled'])"
   ],
   [
    "Workspace Type",
    "tostring(properties['extraProperties']['WorkspaceType'])"
   ]
  ],
  "multi": [
   [
    "Private Endpoints",
    "properties.privateEndpointConnections",
    "",
    "contagem"
   ]
  ]
 },
 {
  "type": "microsoft.web/serverfarms",
  "sheet": "APPSERVICEPLAN",
  "module": "Web/APPServicePlan.ps1",
  "columns": [
   [
    "App Plan OS",
    "tostring(properties['reserved'])"
   ],
   [
    "Apps",
    "tostring(properties['numberOfSites'])"
   ],
   [
    "Apps Type",
    "tostring(properties['kind'])"
   ],
   [
    "Compute Mode",
    "tostring(properties['computeMode'])"
   ],
   [
    "Current Instances",
    "tostring(properties['currentNumberOfWorkers'])"
   ],
   [
    "Intances Size",
    "tostring(properties['currentWorkerSize'])"
   ],
   [
    "Max Instances",
    "tostring(properties['maximumNumberOfWorkers'])"
   ],
   [
    "Zone Redundant",
    "tostring(properties['zoneRedundant'])"
   ]
  ]
 },
 {
  "type": "microsoft.web/sites",
  "sheet": "APPServices",
  "module": "Web/APPServices.ps1",
  "columns": [
   [
    "Admin Enabled",
    "tostring(properties['adminEnabled'])"
   ],
   [
    "App Type",
    "tostring(kind)"
   ],
   [
    "Availability State",
    "tostring(properties['availabilityState'])"
   ],
   [
    "Client Cert Enabled",
    "tostring(properties['clientCertEnabled'])"
   ],
   [
    "Client Cert Mode",
    "tostring(properties['clientCertMode'])"
   ],
   [
    "Container Size",
    "tostring(properties['containerSize'])"
   ],
   [
    "Content Availability State",
    "tostring(properties['contentAvailabilityState'])"
   ],
   [
    "Default Hostname",
    "tostring(properties['defaultHostName'])"
   ],
   [
    "Enabled",
    "tostring(properties['enabled'])"
   ],
   [
    "FTPs Host Name",
    "tostring(properties['ftpsHostName'])"
   ],
   [
    "HTTPS Only",
    "tostring(properties['httpsOnly'])"
   ],
   [
    "Possible Inbound IP Addresses",
    "tostring(properties['possibleInboundIpAddresses'])"
   ],
   [
    "Repository Site Name",
    "tostring(properties['repositorySiteName'])"
   ],
   [
    "Runtime Availability State",
    "tostring(properties['runtimeAvailabilityState'])"
   ],
   [
    "SKU",
    "tostring(properties['sku'])"
   ],
   [
    "Stack",
    "tostring(properties['siteConfig']['linuxFxVersion'])"
   ],
   [
    "State",
    "tostring(properties['state'])"
   ],
   [
    "Subnet",
    "tostring(properties['virtualNetworkSubnetId'])"
   ]
  ],
  "explode": [
   "properties.hostNameSslStates",
   [
    [
     "HostName Type",
     "hostType",
     "ok"
    ],
    [
     "HostNames",
     "name",
     "ok"
    ],
    [
     "SSL State",
     "sslState",
     "ok"
    ]
   ]
  ]
 }
]
