"""Registry of curated Azure resource type configurations.

Each ResourceTypeConfig describes:
- resource_type : exact Azure Resource Graph type string (lowercase)
- sheet_name    : Excel sheet label (max 31 chars)
- columns       : ordered list of (display_name, KQL_extend_expression)
                  The KQL expression is evaluated inside a Resource Graph
                  `extend` clause and should be null-safe (use tostring(),
                  coalesce(), iff(), etc.).

Base columns (Subscription, Resource Group, Nome, Região) are added
automatically by the collector — do NOT include them here.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceTypeConfig:
    resource_type: str
    sheet_name: str
    columns: list[tuple[str, str]]


# ---------------------------------------------------------------------------
# Compute
# ---------------------------------------------------------------------------
_VM = ResourceTypeConfig(
    resource_type="microsoft.compute/virtualmachines",
    sheet_name="Virtual Machines",
    columns=[
        ("Tamanho",             "tostring(properties.hardwareProfile.vmSize)"),
        ("OS",                  "tostring(properties.storageProfile.osDisk.osType)"),
        ("Disco OS (GB)",       "tostring(properties.storageProfile.osDisk.diskSizeGB)"),
        ("Qtd. Discos Dados",   "tostring(array_length(properties.storageProfile.dataDisks))"),
        ("Zonas",               "tostring(zones)"),
        ("Availability Set",    "tostring(properties.availabilitySet.id)"),
        ("Estado Provisioning", "tostring(properties.provisioningState)"),
    ],
)

_VMSS = ResourceTypeConfig(
    resource_type="microsoft.compute/virtualmachinescalesets",
    sheet_name="VM Scale Sets",
    columns=[
        ("Tamanho",          "tostring(properties.virtualMachineProfile.hardwareProfile.vmSize)"),
        ("Capacidade",       "tostring(sku.capacity)"),
        ("Modo",             "tostring(properties.orchestrationMode)"),
        ("Upgrade Policy",   "tostring(properties.upgradePolicy.mode)"),
        ("Zonas",            "tostring(zones)"),
        ("Overprovision",    "tostring(properties.overprovision)"),
    ],
)

_DISK = ResourceTypeConfig(
    resource_type="microsoft.compute/disks",
    sheet_name="Managed Disks",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Tamanho (GB)",     "tostring(properties.diskSizeGB)"),
        ("Tipo OS",          "tostring(properties.osType)"),
        ("Estado",           "tostring(properties.diskState)"),
        ("Criptografia",     "tostring(properties.encryption.type)"),
        ("Acesso Público",   "tostring(properties.networkAccessPolicy)"),
        ("Zonas",            "tostring(zones)"),
    ],
)

_AKS = ResourceTypeConfig(
    resource_type="microsoft.containerservice/managedclusters",
    sheet_name="AKS",
    columns=[
        ("Versão K8s",       "tostring(properties.kubernetesVersion)"),
        ("SKU Tier",         "tostring(sku.tier)"),
        ("Qtd. Node Pools",  "tostring(array_length(properties.agentPoolProfiles))"),
        ("Network Plugin",   "tostring(properties.networkProfile.networkPlugin)"),
        ("Network Policy",   "tostring(properties.networkProfile.networkPolicy)"),
        ("Cluster Privado",  "tostring(properties.apiServerAccessProfile.enablePrivateCluster)"),
        ("RBAC",             "tostring(properties.enableRBAC)"),
        ("OIDC Issuer",      "tostring(properties.oidcIssuerProfile.enabled)"),
        ("Workload Identity","tostring(properties.securityProfile.workloadIdentity.enabled)"),
    ],
)

_ACR = ResourceTypeConfig(
    resource_type="microsoft.containerregistry/registries",
    sheet_name="ACR",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Login Server",     "tostring(properties.loginServer)"),
        ("Admin User",       "tostring(properties.adminUserEnabled)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Zone Redundancy",  "tostring(properties.zoneRedundancy)"),
        ("Data Endpoint",    "tostring(properties.dataEndpointEnabled)"),
    ],
)

_ACI = ResourceTypeConfig(
    resource_type="microsoft.containerinstance/containergroups",
    sheet_name="Container Instances",
    columns=[
        ("OS Type",          "tostring(properties.osType)"),
        ("Restart Policy",   "tostring(properties.restartPolicy)"),
        ("Qtd. Containers",  "tostring(array_length(properties.containers))"),
        ("IP Type",          "tostring(properties.ipAddress.type)"),
        ("IP",               "tostring(properties.ipAddress.ip)"),
        ("SKU",              "tostring(sku)"),
    ],
)

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
_STORAGE = ResourceTypeConfig(
    resource_type="microsoft.storage/storageaccounts",
    sheet_name="Storage Accounts",
    columns=[
        ("Kind",                  "tostring(kind)"),
        ("SKU",                   "tostring(sku.name)"),
        ("Access Tier",           "tostring(properties.accessTier)"),
        ("HTTPS Only",            "tostring(properties.supportsHttpsTrafficOnly)"),
        ("Acesso Público (Blob)", "tostring(properties.allowBlobPublicAccess)"),
        ("TLS Mínimo",            "tostring(properties.minimumTlsVersion)"),
        ("Qtd. Private Endpoints","tostring(array_length(properties.privateEndpointConnections))"),
        ("Allow Shared Key",      "tostring(properties.allowSharedKeyAccess)"),
        ("Soft Delete Blobs",     "tostring(properties.blobServiceProperties.deleteRetentionPolicy.enabled)"),
    ],
)

# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------
_SQL_SERVER = ResourceTypeConfig(
    resource_type="microsoft.sql/servers",
    sheet_name="SQL Servers",
    columns=[
        ("Versão",           "tostring(properties.version)"),
        ("Admin Login",      "tostring(properties.administratorLogin)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("TLS Mínimo",       "tostring(properties.minimalTlsVersion)"),
        ("Entra Auth Only",  "tostring(properties.administrators.azureADOnlyAuthentication)"),
    ],
)

_SQL_DB = ResourceTypeConfig(
    resource_type="microsoft.sql/servers/databases",
    sheet_name="SQL Databases",
    columns=[
        ("Servidor",         "tostring(split(id,'/')[8])"),
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("Capacidade",       "tostring(sku.capacity)"),
        ("Tamanho Máx (GB)", "tostring(toint(properties.maxSizeBytes) / 1073741824)"),
        ("Zone Redundant",   "tostring(properties.zoneRedundant)"),
        ("License Type",     "tostring(properties.licenseType)"),
        ("Read Scale",       "tostring(properties.readScale)"),
    ],
)

_SQL_POOL = ResourceTypeConfig(
    resource_type="microsoft.sql/servers/elasticpools",
    sheet_name="SQL Elastic Pools",
    columns=[
        ("Servidor",         "tostring(split(id,'/')[8])"),
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("Capacidade",       "tostring(sku.capacity)"),
        ("Tamanho Máx (GB)", "tostring(toint(properties.maxSizeBytes) / 1073741824)"),
        ("Zone Redundant",   "tostring(properties.zoneRedundant)"),
    ],
)

_MYSQL = ResourceTypeConfig(
    resource_type="microsoft.dbformysql/flexibleservers",
    sheet_name="MySQL Flexible",
    columns=[
        ("Versão",              "tostring(properties.version)"),
        ("SKU",                 "tostring(sku.name)"),
        ("Tier",                "tostring(sku.tier)"),
        ("Storage (GB)",        "tostring(properties.storage.storageSizeGB)"),
        ("HA Mode",             "tostring(properties.highAvailability.mode)"),
        ("Retenção Backup",     "tostring(properties.backup.backupRetentionDays)"),
        ("Geo-Backup",          "tostring(properties.backup.geoRedundantBackup)"),
        ("Acesso Público",      "tostring(properties.network.publicNetworkAccess)"),
    ],
)

_POSTGRES = ResourceTypeConfig(
    resource_type="microsoft.dbforpostgresql/flexibleservers",
    sheet_name="PostgreSQL Flexible",
    columns=[
        ("Versão",              "tostring(properties.version)"),
        ("SKU",                 "tostring(sku.name)"),
        ("Tier",                "tostring(sku.tier)"),
        ("Storage (GB)",        "tostring(properties.storage.storageSizeGB)"),
        ("HA Mode",             "tostring(properties.highAvailability.mode)"),
        ("Retenção Backup",     "tostring(properties.backup.backupRetentionDays)"),
        ("Geo-Backup",          "tostring(properties.backup.geoRedundantBackup)"),
        ("Acesso Público",      "tostring(properties.network.publicNetworkAccess)"),
    ],
)

_COSMOS = ResourceTypeConfig(
    resource_type="microsoft.documentdb/databaseaccounts",
    sheet_name="Cosmos DB",
    columns=[
        ("API",              "tostring(kind)"),
        ("Consistência",     "tostring(properties.consistencyPolicy.defaultConsistencyLevel)"),
        ("Qtd. Regiões",     "tostring(array_length(properties.locations))"),
        ("Multi-Write",      "tostring(properties.enableMultipleWriteLocations)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Free Tier",        "tostring(properties.enableFreeTier)"),
        ("Backup Mode",      "tostring(properties.backupPolicy.type)"),
    ],
)

_REDIS = ResourceTypeConfig(
    resource_type="microsoft.cache/redis",
    sheet_name="Redis Cache",
    columns=[
        ("SKU",              "tostring(properties.sku.name)"),
        ("Family",           "tostring(properties.sku.family)"),
        ("Capacity",         "tostring(properties.sku.capacity)"),
        ("Non-SSL Port",     "tostring(properties.enableNonSslPort)"),
        ("TLS Mínimo",       "tostring(properties.minimumTlsVersion)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Versão Redis",     "tostring(properties.redisVersion)"),
    ],
)

# ---------------------------------------------------------------------------
# App Platform
# ---------------------------------------------------------------------------
_ASP = ResourceTypeConfig(
    resource_type="microsoft.web/serverfarms",
    sheet_name="App Service Plans",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("Workers",          "tostring(sku.capacity)"),
        ("Max Workers",      "tostring(properties.maximumNumberOfWorkers)"),
        ("Zone Redundant",   "tostring(properties.zoneRedundant)"),
        ("Per-Site Scaling", "tostring(properties.perSiteScaling)"),
        ("OS",               "tostring(kind)"),
    ],
)

_WEBAPP = ResourceTypeConfig(
    resource_type="microsoft.web/sites",
    sheet_name="App Services",
    columns=[
        ("Kind",             "tostring(kind)"),
        ("Estado",           "tostring(properties.state)"),
        ("HTTPS Only",       "tostring(properties.httpsOnly)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("TLS Mínimo",       "tostring(properties.siteConfig.minTlsVersion)"),
        ("Hostname",         "tostring(properties.defaultHostName)"),
        ("App Service Plan", "tostring(properties.serverFarmId)"),
        ("Client Cert",      "tostring(properties.clientCertEnabled)"),
    ],
)

_APIM = ResourceTypeConfig(
    resource_type="microsoft.apimanagement/service",
    sheet_name="API Management",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Capacidade",       "tostring(sku.capacity)"),
        ("VNet Type",        "tostring(properties.virtualNetworkType)"),
        ("Gateway URL",      "tostring(properties.gatewayUrl)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Platform Version", "tostring(properties.platformVersion)"),
    ],
)

_FUNCAPP = ResourceTypeConfig(
    resource_type="microsoft.web/sites/functions",
    sheet_name="Function Apps",
    columns=[
        ("Kind",             "tostring(kind)"),
        ("Estado",           "tostring(properties.state)"),
        ("HTTPS Only",       "tostring(properties.httpsOnly)"),
        ("Hostname",         "tostring(properties.defaultHostName)"),
        ("Runtime",          "tostring(properties.siteConfig.linuxFxVersion)"),
    ],
)

_LOGIC = ResourceTypeConfig(
    resource_type="microsoft.logic/workflows",
    sheet_name="Logic Apps",
    columns=[
        ("Estado",           "tostring(properties.state)"),
        ("SKU",              "tostring(sku.name)"),
        ("Access Endpoint",  "tostring(properties.accessEndpoint)"),
        ("Endpoint Config",  "tostring(properties.endpointsConfiguration.workflow.outgoingIpAddresses)"),
    ],
)

# ---------------------------------------------------------------------------
# Security & Identity
# ---------------------------------------------------------------------------
_KV = ResourceTypeConfig(
    resource_type="microsoft.keyvault/vaults",
    sheet_name="Key Vaults",
    columns=[
        ("SKU",              "tostring(properties.sku.name)"),
        ("Soft Delete",      "tostring(properties.enableSoftDelete)"),
        ("Retenção (dias)",  "tostring(properties.softDeleteRetentionInDays)"),
        ("Purge Protection", "tostring(properties.enablePurgeProtection)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Network ACL",      "tostring(properties.networkAcls.defaultAction)"),
        ("RBAC Auth",        "tostring(properties.enableRbacAuthorization)"),
    ],
)

_UMI = ResourceTypeConfig(
    resource_type="microsoft.managedidentity/userassignedidentities",
    sheet_name="User Managed Identities",
    columns=[
        ("Client ID",    "tostring(properties.clientId)"),
        ("Principal ID", "tostring(properties.principalId)"),
        ("Tenant ID",    "tostring(properties.tenantId)"),
    ],
)

# ---------------------------------------------------------------------------
# Networking
# ---------------------------------------------------------------------------
_VNET = ResourceTypeConfig(
    resource_type="microsoft.network/virtualnetworks",
    sheet_name="Virtual Networks",
    columns=[
        ("Address Space",    "tostring(properties.addressSpace.addressPrefixes)"),
        ("Qtd. Subnets",     "tostring(array_length(properties.subnets))"),
        ("DDoS Protection",  "tostring(properties.enableDdosProtection)"),
        ("Qtd. Peerings",    "tostring(array_length(properties.virtualNetworkPeerings))"),
        ("DNS Servers",      "tostring(properties.dhcpOptions.dnsServers)"),
    ],
)

_NSG = ResourceTypeConfig(
    resource_type="microsoft.network/networksecuritygroups",
    sheet_name="NSGs",
    columns=[
        ("Regras Custom",        "tostring(array_length(properties.securityRules))"),
        ("Regras Default",       "tostring(array_length(properties.defaultSecurityRules))"),
        ("NICs Associadas",      "tostring(array_length(properties.networkInterfaces))"),
        ("Subnets Associadas",   "tostring(array_length(properties.subnets))"),
    ],
)

_PIP = ResourceTypeConfig(
    resource_type="microsoft.network/publicipaddresses",
    sheet_name="Public IPs",
    columns=[
        ("SKU",          "tostring(sku.name)"),
        ("Alocação",     "tostring(properties.publicIPAllocationMethod)"),
        ("Endereço IP",  "tostring(properties.ipAddress)"),
        ("Versão IP",    "tostring(properties.publicIPAddressVersion)"),
        ("Zonas",        "tostring(zones)"),
        ("DNS Label",    "tostring(properties.dnsSettings.domainNameLabel)"),
    ],
)

_LB = ResourceTypeConfig(
    resource_type="microsoft.network/loadbalancers",
    sheet_name="Load Balancers",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("Frontend IPs",     "tostring(array_length(properties.frontendIPConfigurations))"),
        ("Backend Pools",    "tostring(array_length(properties.backendAddressPools))"),
        ("Regras LB",        "tostring(array_length(properties.loadBalancingRules))"),
        ("Probes",           "tostring(array_length(properties.probes))"),
    ],
)

_AGW = ResourceTypeConfig(
    resource_type="microsoft.network/applicationgateways",
    sheet_name="App Gateways",
    columns=[
        ("SKU",              "tostring(properties.sku.name)"),
        ("Tier",             "tostring(properties.sku.tier)"),
        ("Capacidade",       "tostring(properties.sku.capacity)"),
        ("WAF Enabled",      "tostring(properties.webApplicationFirewallConfiguration.enabled)"),
        ("WAF Mode",         "tostring(properties.webApplicationFirewallConfiguration.firewallMode)"),
        ("Autoscale Min",    "tostring(properties.autoscaleConfiguration.minCapacity)"),
        ("Autoscale Max",    "tostring(properties.autoscaleConfiguration.maxCapacity)"),
    ],
)

_FIREWALL = ResourceTypeConfig(
    resource_type="microsoft.network/azurefirewalls",
    sheet_name="Azure Firewalls",
    columns=[
        ("SKU Tier",           "tostring(properties.sku.tier)"),
        ("Threat Intel Mode",  "tostring(properties.threatIntelMode)"),
        ("Firewall Policy",    "tostring(properties.firewallPolicy.id)"),
        ("IP Configs",         "tostring(array_length(properties.ipConfigurations))"),
    ],
)

_VPNGW = ResourceTypeConfig(
    resource_type="microsoft.network/virtualnetworkgateways",
    sheet_name="VPN Gateways",
    columns=[
        ("SKU",          "tostring(properties.sku.name)"),
        ("Tier",         "tostring(properties.sku.tier)"),
        ("Tipo",         "tostring(properties.gatewayType)"),
        ("VPN Type",     "tostring(properties.vpnType)"),
        ("Active-Active","tostring(properties.activeActive)"),
        ("BGP",          "tostring(properties.enableBgp)"),
        ("Geração",      "tostring(properties.vpnGatewayGeneration)"),
    ],
)

_PE = ResourceTypeConfig(
    resource_type="microsoft.network/privateendpoints",
    sheet_name="Private Endpoints",
    columns=[
        ("Subnet",             "tostring(properties.subnet.id)"),
        ("Serviço Destino",    "tostring(properties.privateLinkServiceConnections[0].privateLinkServiceId)"),
        ("Sub-recurso",        "tostring(properties.privateLinkServiceConnections[0].groupIds[0])"),
        ("Status Conexão",     "tostring(properties.privateLinkServiceConnections[0].privateLinkServiceConnectionState.status)"),
    ],
)

_PDNS = ResourceTypeConfig(
    resource_type="microsoft.network/privatednszones",
    sheet_name="Private DNS Zones",
    columns=[
        ("VNet Links",   "tostring(properties.numberOfVirtualNetworkLinks)"),
        ("Record Sets",  "tostring(properties.numberOfRecordSets)"),
        ("Max Links",    "tostring(properties.maxNumberOfVirtualNetworkLinks)"),
    ],
)

_BASTIONHOST = ResourceTypeConfig(
    resource_type="microsoft.network/bastionhosts",
    sheet_name="Bastion Hosts",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Qtd. IP Configs",  "tostring(array_length(properties.ipConfigurations))"),
        ("Scale Units",      "tostring(properties.scaleUnits)"),
        ("Tunneling",        "tostring(properties.enableTunneling)"),
        ("Native Client",    "tostring(properties.enableIpConnect)"),
    ],
)

# ---------------------------------------------------------------------------
# Monitoring & Operations
# ---------------------------------------------------------------------------
_LAW = ResourceTypeConfig(
    resource_type="microsoft.operationalinsights/workspaces",
    sheet_name="Log Analytics",
    columns=[
        ("SKU",              "tostring(properties.sku.name)"),
        ("Retenção (dias)",  "tostring(properties.retentionInDays)"),
        ("Daily Cap (GB)",   "tostring(properties.workspaceCapping.dailyQuotaGb)"),
        ("Ingestão Pública", "tostring(properties.publicNetworkAccessForIngestion)"),
        ("Query Pública",    "tostring(properties.publicNetworkAccessForQuery)"),
    ],
)

_APPINS = ResourceTypeConfig(
    resource_type="microsoft.insights/components",
    sheet_name="App Insights",
    columns=[
        ("Tipo de App",      "tostring(properties.Application_Type)"),
        ("Workspace",        "tostring(properties.WorkspaceResourceId)"),
        ("Sampling %",       "tostring(properties.SamplingPercentage)"),
        ("Retenção (dias)",  "tostring(properties.RetentionInDays)"),
        ("Ingestão Pública", "tostring(properties.publicNetworkAccessForIngestion)"),
        ("Query Pública",    "tostring(properties.publicNetworkAccessForQuery)"),
    ],
)

_AUTO = ResourceTypeConfig(
    resource_type="microsoft.automation/automationaccounts",
    sheet_name="Automation Accounts",
    columns=[
        ("SKU",                     "tostring(properties.sku.name)"),
        ("Acesso Público",          "tostring(properties.publicNetworkAccess)"),
        ("Local Auth Desabilitado", "tostring(properties.disableLocalAuth)"),
        ("Estado",                  "tostring(properties.state)"),
    ],
)

_RSV = ResourceTypeConfig(
    resource_type="microsoft.recoveryservices/vaults",
    sheet_name="Recovery Services",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Imutabilidade",    "tostring(properties.securitySettings.immutabilitySettings.state)"),
        ("Soft Delete",      "tostring(properties.securitySettings.softDeleteSettings.softDeleteState)"),
    ],
)

# ---------------------------------------------------------------------------
# Messaging & Integration
# ---------------------------------------------------------------------------
_SB = ResourceTypeConfig(
    resource_type="microsoft.servicebus/namespaces",
    sheet_name="Service Bus",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("Capacidade",       "tostring(sku.capacity)"),
        ("Zone Redundant",   "tostring(properties.zoneRedundant)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("TLS Mínimo",       "tostring(properties.minimumTlsVersion)"),
        ("Local Auth",       "tostring(properties.disableLocalAuth)"),
    ],
)

_EH = ResourceTypeConfig(
    resource_type="microsoft.eventhub/namespaces",
    sheet_name="Event Hubs",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Tier",             "tostring(sku.tier)"),
        ("TUs",              "tostring(sku.capacity)"),
        ("Auto-Inflate",     "tostring(properties.isAutoInflateEnabled)"),
        ("Max TUs",          "tostring(properties.maximumThroughputUnits)"),
        ("Zone Redundant",   "tostring(properties.zoneRedundant)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("TLS Mínimo",       "tostring(properties.minimumTlsVersion)"),
    ],
)

# ---------------------------------------------------------------------------
# AI & Cognitive
# ---------------------------------------------------------------------------
_COG = ResourceTypeConfig(
    resource_type="microsoft.cognitiveservices/accounts",
    sheet_name="Cognitive Services",
    columns=[
        ("Kind",             "tostring(kind)"),
        ("SKU",              "tostring(sku.name)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Network ACL",      "tostring(properties.networkAcls.defaultAction)"),
        ("Custom Domain",    "tostring(properties.customSubDomainName)"),
        ("Endpoint",         "tostring(properties.endpoint)"),
    ],
)

_AISEARCH = ResourceTypeConfig(
    resource_type="microsoft.search/searchservices",
    sheet_name="AI Search",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Réplicas",         "tostring(properties.replicaCount)"),
        ("Partições",        "tostring(properties.partitionCount)"),
        ("Hosting Mode",     "tostring(properties.hostingMode)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Auth Options",     "tostring(properties.authOptions)"),
    ],
)

_ML = ResourceTypeConfig(
    resource_type="microsoft.machinelearningservices/workspaces",
    sheet_name="Azure ML",
    columns=[
        ("SKU",              "tostring(sku.name)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("HBI Workspace",    "tostring(properties.hbiWorkspace)"),
        ("Storage Account",  "tostring(properties.storageAccount)"),
        ("Key Vault",        "tostring(properties.keyVault)"),
        ("Container Reg.",   "tostring(properties.containerRegistry)"),
    ],
)

# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
_SYNAPSE = ResourceTypeConfig(
    resource_type="microsoft.synapse/workspaces",
    sheet_name="Synapse",
    columns=[
        ("SQL Admin",        "tostring(properties.sqlAdministratorLogin)"),
        ("Acesso Público",   "tostring(properties.publicNetworkAccess)"),
        ("Managed VNet",     "tostring(properties.managedVirtualNetwork)"),
        ("Data Exfil Prot.", "tostring(properties.managedVirtualNetworkSettings.preventDataExfiltration)"),
    ],
)

# ---------------------------------------------------------------------------
# Ordered registry — defines report tab order
# ---------------------------------------------------------------------------
RESOURCE_CONFIGS: list[ResourceTypeConfig] = [
    _VM,
    _VMSS,
    _DISK,
    _AKS,
    _ACR,
    _ACI,
    _STORAGE,
    _SQL_SERVER,
    _SQL_DB,
    _SQL_POOL,
    _MYSQL,
    _POSTGRES,
    _COSMOS,
    _REDIS,
    _ASP,
    _WEBAPP,
    _APIM,
    _LOGIC,
    _KV,
    _UMI,
    _VNET,
    _NSG,
    _PIP,
    _LB,
    _AGW,
    _FIREWALL,
    _VPNGW,
    _PE,
    _PDNS,
    _BASTIONHOST,
    _LAW,
    _APPINS,
    _AUTO,
    _RSV,
    _SB,
    _EH,
    _COG,
    _AISEARCH,
    _ML,
    _SYNAPSE,
]

# Lookup by resource type (lowercase)
CONFIGS_BY_TYPE: dict[str, ResourceTypeConfig] = {
    c.resource_type: c for c in RESOURCE_CONFIGS
}

# ---------------------------------------------------------------------------
# Friendly-name resolution
# ---------------------------------------------------------------------------
# Supplementary human-readable names for common resource types that are NOT
# part of the curated RESOURCE_CONFIGS above. Keys are the exact Azure
# Resource Graph type strings (always lowercase).
_EXTRA_FRIENDLY_NAMES: dict[str, str] = {
    # Compute
    "microsoft.compute/availabilitysets": "Availability Sets",
    "microsoft.compute/snapshots": "Snapshots",
    "microsoft.compute/images": "Images",
    "microsoft.compute/galleries": "Compute Galleries",
    "microsoft.compute/sshpublickeys": "SSH Keys",
    "microsoft.compute/diskencryptionsets": "Disk Encryption Sets",
    "microsoft.compute/virtualmachines/extensions": "VM Extensions",
    "microsoft.sqlvirtualmachine/sqlvirtualmachines": "SQL VMs",
    "microsoft.classiccompute/virtualmachines": "VMs (Classic)",
    # Networking
    "microsoft.network/routetables": "Route Tables",
    "microsoft.network/natgateways": "NAT Gateways",
    "microsoft.network/networkinterfaces": "Network Interfaces",
    "microsoft.network/networkwatchers": "Network Watchers",
    "microsoft.network/dnszones": "DNS Zones",
    "microsoft.network/trafficmanagerprofiles": "Traffic Manager",
    "microsoft.network/frontdoors": "Front Door (Classic)",
    "microsoft.cdn/profiles": "Front Door / CDN",
    "microsoft.network/connections": "VNet Connections",
    "microsoft.network/localnetworkgateways": "Local Network Gateways",
    "microsoft.network/privatelinkservices": "Private Link Services",
    "microsoft.network/ddosprotectionplans": "DDoS Protection Plans",
    "microsoft.network/expressroutecircuits": "ExpressRoute Circuits",
    "microsoft.network/applicationsecuritygroups": "App Security Groups",
    "microsoft.network/ipgroups": "IP Groups",
    "microsoft.network/firewallpolicies": "Firewall Policies",
    "microsoft.network/virtualnetworks/subnets": "Subnets",
    "microsoft.network/virtualnetworks/virtualnetworkpeerings": "VNet Peerings",
    # Data & analytics
    "microsoft.databricks/workspaces": "Databricks",
    "microsoft.kusto/clusters": "Data Explorer Clusters",
    "microsoft.datafactory/factories": "Data Factory",
    # Web & integration
    "microsoft.web/staticsites": "Static Web Apps",
    "microsoft.web/connections": "API Connections",
    "microsoft.web/certificates": "App Service Certs",
    "microsoft.eventgrid/systemtopics": "Event Grid System Topics",
    "microsoft.eventgrid/topics": "Event Grid Topics",
    "microsoft.eventgrid/domains": "Event Grid Domains",
    "microsoft.signalrservice/signalr": "SignalR",
    "microsoft.signalrservice/webpubsub": "Web PubSub",
    "microsoft.appconfiguration/configurationstores": "App Configuration",
    "microsoft.app/managedenvironments": "Container Apps Env",
    "microsoft.app/containerapps": "Container Apps",
    # Management & monitoring
    "microsoft.automation/automationaccounts/runbooks": "Runbooks",
    "microsoft.insights/actiongroups": "Action Groups",
    "microsoft.insights/activitylogalerts": "Activity Log Alerts",
    "microsoft.insights/metricalerts": "Metric Alerts",
    "microsoft.insights/scheduledqueryrules": "Scheduled Query Rules",
    "microsoft.insights/webtests": "Web Tests",
    "microsoft.insights/datacollectionrules": "Data Collection Rules",
    "microsoft.insights/datacollectionendpoints": "Data Collection Endpoints",
    "microsoft.dashboard/grafana": "Grafana",
    "microsoft.portal/dashboards": "Portal Dashboards",
    "microsoft.operationsmanagement/solutions": "OMS Solutions",
    "microsoft.resources/templatespecs": "Template Specs",
    "microsoft.resources/deploymentscripts": "Deployment Scripts",
    # Other common
    "microsoft.batch/batchaccounts": "Batch Accounts",
    "microsoft.desktopvirtualization/hostpools": "AVD Host Pools",
    "microsoft.desktopvirtualization/workspaces": "AVD Workspaces",
    "microsoft.desktopvirtualization/applicationgroups": "AVD App Groups",
    # Azure Arc — hybrid compute & data (frequently the highest-volume types)
    "microsoft.hybridcompute/machines": "Arc Servers",
    "microsoft.hybridcompute/machines/extensions": "Arc Server Extensions",
    "microsoft.hybridcompute/machines/licenseprofiles": "Arc License Profiles",
    "microsoft.azurearcdata/sqlserverinstances": "Arc SQL Server Instances",
    "microsoft.azurearcdata/sqlserverinstances/databases": "Arc SQL Databases",
    "microsoft.azurearcdata/sqlserverinstances/availabilitygroups": "Arc SQL Availability Groups",
    "microsoft.azurearcdata/sqlmanagedinstances": "Arc SQL Managed Instances",
    "microsoft.kubernetes/connectedclusters": "Arc Kubernetes Clusters",
    # Alerts & monitoring extras
    "microsoft.alertsmanagement/smartdetectoralertrules": "Smart Detector Alert Rules",
    "microsoft.alertsmanagement/prometheusrulegroups": "Prometheus Rule Groups",
    "microsoft.insights/workbooks": "Workbooks",
    "microsoft.insights/autoscalesettings": "Autoscale Settings",
    "microsoft.monitor/accounts": "Monitor Workspaces",
    "microsoft.operationalinsights/querypacks": "Query Packs",
    "microsoft.dashboard/dashboards": "Grafana Dashboards",
    # Networking child/extra types
    "microsoft.network/privatednszones/virtualnetworklinks": "Private DNS VNet Links",
    "microsoft.network/networkintentpolicies": "Network Intent Policies",
    "microsoft.network/networkwatchers/connectionmonitors": "Connection Monitors",
    "microsoft.network/networkwatchers/flowlogs": "NSG Flow Logs",
    "microsoft.network/publicipprefixes": "Public IP Prefixes",
    # Compute extras
    "microsoft.compute/restorepointcollections": "Restore Point Collections",
    "microsoft.compute/galleries/images": "Gallery Image Definitions",
    "microsoft.compute/galleries/images/versions": "Gallery Image Versions",
    "microsoft.maintenance/maintenanceconfigurations": "Maintenance Configurations",
    # Data & messaging extras
    "microsoft.cache/redisenterprise": "Redis Enterprise",
    "microsoft.streamanalytics/streamingjobs": "Stream Analytics Jobs",
    "microsoft.notificationhubs/namespaces": "Notification Hub Namespaces",
    "microsoft.notificationhubs/namespaces/notificationhubs": "Notification Hubs",
    "microsoft.netapp/netappaccounts/capacitypools/volumes": "NetApp Volumes",
    "microsoft.sql/managedinstances": "SQL Managed Instances",
    "microsoft.sql/managedinstances/databases": "SQL MI Databases",
    # Registry / containers extras
    "microsoft.containerregistry/registries/replications": "ACR Replications",
    "microsoft.containerregistry/registries/webhooks": "ACR Webhooks",
    "microsoft.redhatopenshift/openshiftclusters": "ARO Clusters",
    # AI extras
    "microsoft.cognitiveservices/accounts/projects": "AI Foundry Projects",
    "microsoft.machinelearningservices/workspaces/onlineendpoints/deployments": "ML Online Deployments",
    "microsoft.botservice/botservices": "Bot Services",
    # Dev / lab / misc
    "microsoft.devtestlab/schedules": "DevTest Schedules",
    "microsoft.devcenter/devcenters": "Dev Centers",
    "microsoft.devcenter/projects": "Dev Center Projects",
    "microsoft.databricks/accessconnectors": "Databricks Access Connectors",
    "microsoft.chaos/experiments": "Chaos Experiments",
    "microsoft.loadtestservice/loadtests": "Load Tests",
    "microsoft.migrate/movecollections": "Move Collections",
    "microsoft.web/sites/slots": "App Service Slots",
    "microsoft.cdn/profiles/endpoints": "CDN Endpoints",
    "microsoft.resources/templatespecs/versions": "Template Spec Versions",
    "microsoft.visualstudio/account": "Visual Studio Accounts",
    # --- Long tail: explicit names to avoid jammed camelCase fallbacks ---
    # Networking
    "microsoft.network/frontdoorwebapplicationfirewallpolicies": "Front Door WAF Policies",
    "microsoft.network/applicationgatewaywebapplicationfirewallpolicies": "App Gateway WAF Policies",
    "microsoft.network/networkprofiles": "Network Profiles",
    "microsoft.network/networksecurityperimeters": "Network Security Perimeters",
    "microsoft.network/vpnserverconfigurations": "VPN Server Configurations",
    "microsoft.network/dnsresolvers": "DNS Private Resolvers",
    "microsoft.network/serviceendpointpolicies": "Service Endpoint Policies",
    "microsoft.cdn/profiles/afdendpoints": "Front Door Endpoints",
    # Compute
    "microsoft.compute/proximityplacementgroups": "Proximity Placement Groups",
    "microsoft.compute/virtualmachines/runcommands": "VM Run Commands",
    "microsoft.sqlvirtualmachine/sqlvirtualmachinegroups": "SQL VM Groups",
    # Storage & data
    "microsoft.netapp/netappaccounts": "NetApp Accounts",
    "microsoft.netapp/netappaccounts/capacitypools": "NetApp Capacity Pools",
    "microsoft.documentdb/mongoclusters": "Cosmos DB for MongoDB (vCore)",
    "microsoft.documentdb/cassandraclusters": "Managed Cassandra Clusters",
    "microsoft.datamigration/sqlmigrationservices": "SQL Migration Services",
    "microsoft.sql/virtualclusters": "SQL Virtual Clusters",
    "microsoft.sql/servers/jobagents": "SQL Job Agents",
    "microsoft.datashare/accounts": "Data Share Accounts",
    "microsoft.storagemover/storagemovers": "Storage Movers",
    "microsoft.storagediscovery/storagediscoveryworkspaces": "Storage Discovery Workspaces",
    # Analytics & AI
    "microsoft.fabric/capacities": "Fabric Capacities",
    "microsoft.powerbidedicated/capacities": "Power BI Embedded Capacities",
    "microsoft.videoindexer/accounts": "Video Indexer Accounts",
    "microsoft.maps/accounts": "Azure Maps Accounts",
    "microsoft.purview/accounts": "Purview Accounts",
    "microsoft.securitycopilot/capacities": "Security Copilot Capacities",
    "microsoft.machinelearningservices/workspaces/onlineendpoints": "ML Online Endpoints",
    "microsoft.machinelearningservices/workspaces/batchendpoints": "ML Batch Endpoints",
    "microsoft.machinelearningservices/workspaces/batchendpoints/deployments": "ML Batch Deployments",
    # Monitoring, security & management
    "microsoft.cloudhealth/healthmodels": "Cloud Health Models",
    "microsoft.security/securityconnectors": "Defender Security Connectors",
    "microsoft.insights/privatelinkscopes": "Azure Monitor Private Link Scopes",
    "microsoft.hybridcompute/privatelinkscopes": "Arc Private Link Scopes",
    "microsoft.kubernetesconfiguration/privatelinkscopes": "K8s Config Private Link Scopes",
    "microsoft.alertsmanagement/actionrules": "Alert Processing Rules",
    "microsoft.dataprotection/backupvaults": "Backup Vaults",
    "microsoft.resourcegraph/queries": "Resource Graph Queries",
    "microsoft.serviceshub/connectors": "Services Hub Connectors",
    "microsoft.portalservices/dashboards": "Portal Dashboards",
    "microsoft.dashboard/grafana/managedprivateendpoints": "Grafana Managed Private Endpoints",
    # Migrate / off-Azure
    "microsoft.migrate/migrateprojects": "Migrate Projects",
    "microsoft.offazure/vmwaresites": "Migrate VMware Sites",
    "microsoft.offazure/serversites": "Migrate Server Sites",
    # Identity & directories
    "microsoft.azureactivedirectory/b2cdirectories": "Azure AD B2C Directories",
    "microsoft.azureactivedirectory/ciamdirectories": "Entra External ID (CIAM)",
    "microsoft.keyvault/managedhsms": "Managed HSMs",
    # Integration & apps
    "microsoft.logic/integrationaccounts": "Integration Accounts",
    "microsoft.web/customapis": "Logic App Custom APIs",
    "microsoft.communication/communicationservices": "Communication Services",
    "microsoft.communication/emailservices": "Email Communication Services",
    "microsoft.communication/emailservices/domains": "Email Service Domains",
    "microsoft.certificateregistration/certificateorders": "App Service Cert Orders",
    "microsoft.app/agents": "Container Apps Agents",
    # Dev, DevOps & labs
    "microsoft.devopsinfrastructure/pools": "Managed DevOps Pools",
    "microsoft.devtestlab/labs": "DevTest Labs",
    "microsoft.devcenter/devcenters/devboxdefinitions": "Dev Box Definitions",
    "microsoft.devcenter/networkconnections": "Dev Center Network Connections",
    "microsoft.containerservice/fleets": "AKS Fleets",
    "microsoft.desktopvirtualization/scalingplans": "AVD Scaling Plans",
    # Misc
    "microsoft.saas/resources": "SaaS Resources",
    "microsoft.powerplatform/accounts": "Power Platform Accounts",
    "microsoft.operationalinsights/clusters": "Log Analytics Clusters",
    "microsoft.networkfunction/azuretrafficcollectors": "Azure Traffic Collectors",
    "microsoft.networkfunction/azuretrafficcollectors/collectorpolicies": "Traffic Collector Policies",
}


def friendly_resource_name(resource_type: str) -> str:
    """Return a human-readable name for an Azure Resource Graph *resource_type*.

    Resolution order:
      1. Curated RESOURCE_CONFIGS sheet name.
      2. Supplementary _EXTRA_FRIENDLY_NAMES map.
      3. Heuristic fallback: split jammed lowercase leaf using a known token
         vocabulary, prefixing parent/service context for generic leaves.
    """
    if not resource_type:
        return "N/A"
    key = resource_type.lower()
    cfg = CONFIGS_BY_TYPE.get(key)
    if cfg is not None:
        return cfg.sheet_name
    if key in _EXTRA_FRIENDLY_NAMES:
        return _EXTRA_FRIENDLY_NAMES[key]
    return _humanize_type(key)


# Atomic tokens found in Azure resource-type leaf segments. Used to split
# jammed, all-lowercase names (Resource Graph returns types lowercased) into
# readable words. At each position the LONGEST matching token wins.
_KNOWN_TOKENS: tuple[str, ...] = (
    # multi-letter service/domain words
    "notification", "configuration", "configurations", "application", "certificate",
    "certificateorders", "communication", "subscription", "subscriptions",
    "recommendation", "registration", "orchestration", "virtual", "network",
    "networks", "machine", "machines", "security", "connector", "connectors",
    "connection", "connections", "endpoint", "endpoints", "workspace", "workspaces",
    "workbook", "workbooks", "instance", "instances", "resource", "resources",
    "capacity", "capacities", "directory", "directories", "dashboard", "dashboards",
    "definition", "definitions", "deployment", "deployments", "collection",
    "collections", "collector", "collectors", "placement", "proximity", "profile",
    "profiles", "policy", "policies", "firewall", "gateway", "gateways", "front",
    "door", "traffic", "manager", "scaling", "scopes", "scope", "private", "link",
    "links", "public", "prefix", "prefixes", "interface", "interfaces", "server",
    "servers", "service", "services", "account", "accounts", "cluster", "clusters",
    "vault", "vaults", "backup", "storage", "discovery", "mover", "movers",
    "migrate", "migration", "project", "projects", "integration", "resolver",
    "resolvers", "health", "model", "models", "perimeter", "perimeters", "email",
    "domain", "domains", "custom", "runbook", "runbooks", "runcommand",
    "runcommands", "command", "commands", "action", "rules", "rule", "query",
    "queries", "agent", "agents", "order", "orders", "labs", "lab", "pool",
    "pools", "group", "groups", "site", "sites", "slot", "slots", "hub", "hubs",
    "plan", "plans", "job", "jobs", "agents", "fleet", "fleets", "widget",
    "widgets", "endpoint", "web", "sql", "vpn", "dns", "b2c", "ciam", "afd",
    "vmware", "api", "apis", "azure", "managed", "version", "versions", "image",
    "images", "template", "spec", "specs", "batch", "online",
)

# Sorted once, longest-first, so greedy matching prefers the longest token.
_TOKENS_BY_LEN: tuple[str, ...] = tuple(
    sorted(set(_KNOWN_TOKENS), key=len, reverse=True)
)

# Leaf words too generic to stand alone — prefixed with parent/service context.
_GENERIC_LEAVES: frozenset[str] = frozenset({
    "accounts", "account", "capacities", "capacity", "resources", "resource",
    "domains", "domain", "clusters", "cluster", "pools", "pool", "projects",
    "project", "endpoints", "endpoint", "deployments", "deployment", "dashboards",
    "dashboard", "queries", "query", "agents", "agent", "labs", "lab", "services",
    "service", "connectors", "connector", "definitions", "definition", "sites",
    "site", "groups", "group", "rules", "rule",
})

# Provider namespace → short service label for fallback context prefixes.
_PROVIDER_LABELS: dict[str, str] = {
    "microsoft.datashare": "Data Share",
    "microsoft.purview": "Purview",
    "microsoft.maps": "Azure Maps",
    "microsoft.powerplatform": "Power Platform",
    "microsoft.fabric": "Fabric",
    "microsoft.videoindexer": "Video Indexer",
    "microsoft.saas": "SaaS",
}


def _split_tokens(word: str) -> list[str]:
    """Greedily split a jammed lowercase *word*, longest known token first."""
    parts: list[str] = []
    i = 0
    n = len(word)
    while i < n:
        for tok in _TOKENS_BY_LEN:
            if word.startswith(tok, i):
                parts.append(tok)
                i += len(tok)
                break
        else:
            # No known token here: consume until the next token boundary.
            j = i + 1
            while j < n and not any(word.startswith(t, j) for t in _TOKENS_BY_LEN):
                j += 1
            parts.append(word[i:j])
            i = j
    return parts


def _humanize_type(key: str) -> str:
    """Build a readable label for an unmapped resource type string."""
    provider, _, path = key.partition("/")
    segments = path.split("/") if path else []
    leaf = segments[-1] if segments else provider

    words = " ".join(_split_tokens(leaf.replace("-", "").replace("_", ""))).title()

    if leaf in _GENERIC_LEAVES:
        # Prefix with parent segment or provider service for disambiguation.
        if len(segments) >= 2:
            parent = " ".join(_split_tokens(segments[-2])).title()
            words = f"{parent} {words}"
        else:
            label = _PROVIDER_LABELS.get(provider)
            if label:
                words = f"{label} {words}"
            else:
                svc = provider.split(".")[-1]
                words = f"{' '.join(_split_tokens(svc)).title()} {words}"

    return _fix_acronyms(words)


# Words that should be rendered as uppercase acronyms after title-casing.
_ACRONYMS: dict[str, str] = {
    "Dns": "DNS", "Ip": "IP", "Vpn": "VPN", "Sql": "SQL", "Api": "API",
    "Apis": "APIs", "Afd": "AFD", "B2C": "B2C", "B2c": "B2C", "Ciam": "CIAM",
    "Vm": "VM", "Vmss": "VMSS", "Ml": "ML", "Aks": "AKS", "Acr": "ACR",
    "Nsg": "NSG", "Nsgs": "NSGs", "Hsm": "HSM", "Hsms": "HSMs", "Waf": "WAF",
    "Cdn": "CDN", "Aad": "AAD", "Vmware": "VMware", "Saas": "SaaS",
    "Db": "DB", "Pip": "PIP", "Avd": "AVD", "Aro": "ARO",
}


def _fix_acronyms(text: str) -> str:
    """Uppercase known acronyms in an already title-cased *text*."""
    return " ".join(_ACRONYMS.get(w, w) for w in text.split(" "))
