# Tool to create AWS IAM policy based on Tofu modules

It extract all AWS API calls from a Tofu module, it compares this list with the official service reference and splits the operation in Read and Write.
Then it creates a IAM police for them, for EC2 is also splits the writes in server operation and network operation.
By default there's no target, but you can specify a region and a tag, see below:
 
## Setup


```
python3 -m venv tig
pip3 install -r requirements.txt
source bin/activate
```

## Run

```
$ python iam-gen.py waf                                                      
🔹 Service: waf
🔹 Fetching GitHub repo tree...
   Go files found: 75
🔹 Fetching service reference JSON...
   Service reference actions: 77
🔹 Scanning Go files...
   [1/75] internal/service/waf/byte_match_set.go
   [75/75] internal/service/wafv2/web_acl_rule_group_association.go
   Common functions: 69
✅ Wrote waf-read.json (29 actions)
✅ Wrote waf-write.json (40 actions)



$ python3 iam-gen.py ec2 eu-central-1
🔹 Service: ec2
🔹 Region restriction: eu-central-1
🔹 Fetching GitHub repo tree...
   Go files found: 274
🔹 Fetching service reference JSON...
   Service reference actions: 770
🔹 Scanning Go files...
   [1/274] internal/service/ec2/arn.go
   [2/274] internal/service/ec2/consts.go
   [3/274] internal/service/ec2/diff.go
   [4/274] internal/service/ec2/ebs_default_kms_key.go
   [5/274] internal/service/ec2/ebs_default_kms_key_data_source.go
   [6/274] internal/service/ec2/ebs_encryption_by_default.go
   [7/274] internal/service/ec2/ebs_encryption_by_default_data_source.go
   [8/274] internal/service/ec2/ebs_fast_snapshot_restore.go
   [9/274] internal/service/ec2/ebs_snapshot.go
   [274/274] internal/service/ec2/wavelength_carrier_gateway.go
   Common functions: 441
✅ Wrote ec2-read.json (133 actions)
✅ Wrote ec2-write-server.json (72 actions)
✅ Wrote ec2-write-network.json (236 actions)

$
$
$ cat ec2-write-server.json 
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AllocateHosts",
                "ec2:AssociateIamInstanceProfile",
                "ec2:AttachVolume",
                "ec2:CancelCapacityReservation",
                "ec2:CancelSpotFleetRequests",
                "ec2:CancelSpotInstanceRequests",
                "ec2:CopyImage",
                "ec2:CopySnapshot",
                "ec2:CreateCapacityReservation",
                "ec2:CreateFleet",
                "ec2:CreateImage",
                "ec2:CreateInstanceConnectEndpoint",
                "ec2:CreateLaunchTemplate",
                "ec2:CreateLaunchTemplateVersion",
                "ec2:CreatePlacementGroup",
                "ec2:CreateSnapshot",
                "ec2:CreateSpotDatafeedSubscription",
                "ec2:CreateVerifiedAccessInstance",
                "ec2:CreateVolume",
                "ec2:DeleteFleets",
                "ec2:DeleteInstanceConnectEndpoint",
                "ec2:DeleteKeyPair",
                "ec2:DeleteLaunchTemplate",
                "ec2:DeletePlacementGroup",
                "ec2:DeleteSnapshot",
                "ec2:DeleteSpotDatafeedSubscription",
                "ec2:DeleteVerifiedAccessInstance",
                "ec2:DeleteVolume",
                "ec2:DeregisterImage",
                "ec2:DetachVolume",
                "ec2:DisableFastSnapshotRestores",
                "ec2:DisableImageBlockPublicAccess",
                "ec2:DisableImageDeprecation",
                "ec2:DisableSnapshotBlockPublicAccess",
                "ec2:DisassociateIamInstanceProfile",
                "ec2:EnableAllowedImagesSettings",
                "ec2:EnableFastSnapshotRestores",
                "ec2:EnableImageBlockPublicAccess",
                "ec2:EnableImageDeprecation",
                "ec2:EnableSnapshotBlockPublicAccess",
                "ec2:ImportKeyPair",
                "ec2:ImportSnapshot",
                "ec2:ModifyCapacityReservation",
                "ec2:ModifyFleet",
                "ec2:ModifyHosts",
                "ec2:ModifyImageAttribute",
                "ec2:ModifyInstanceAttribute",
                "ec2:ModifyInstanceCapacityReservationAttributes",
                "ec2:ModifyInstanceCreditSpecification",
                "ec2:ModifyInstanceMaintenanceOptions",
                "ec2:ModifyInstanceMetadataDefaults",
                "ec2:ModifyInstanceMetadataOptions",
                "ec2:ModifyLaunchTemplate",
                "ec2:ModifySnapshotAttribute",
                "ec2:ModifySnapshotTier",
                "ec2:ModifySpotFleetRequest",
                "ec2:ModifyVerifiedAccessInstance",
                "ec2:ModifyVerifiedAccessInstanceLoggingConfiguration",
                "ec2:ModifyVolume",
                "ec2:MonitorInstances",
                "ec2:RegisterImage",
                "ec2:ReleaseHosts",
                "ec2:ReplaceIamInstanceProfileAssociation",
                "ec2:ReplaceImageCriteriaInAllowedImagesSettings",
                "ec2:RequestSpotFleet",
                "ec2:RequestSpotInstances",
                "ec2:RestoreSnapshotTier",
                "ec2:RunInstances",
                "ec2:StartInstances",
                "ec2:StopInstances",
                "ec2:TerminateInstances",
                "ec2:UnmonitorInstances"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "eu-central-1"
                }
            }
        }
    ]
}

```

Adding the ENV tag limit

```
$ python3 iam-gene.py route53 eu-central-1 Env=Dev
🔹 Service: route53
🔹 Region restriction: eu-central-1
🔹 RequestTag: Env = ['Dev']
🔹 Fetching GitHub repo tree...
   Go files found: 100
🔹 Fetching service reference JSON...
   Service reference actions: 71
🔹 Scanning Go files...
   [1/100] internal/service/route53/accelerated_recovery_status.go
   [2/100] internal/service/route53/change_info.go
   [3/100] internal/service/route53/cidr_collection.go
   [4/100] internal/service/route53/cidr_location.go
   [5/100] internal/service/route53/clean.go
   [6/100] internal/service/route53/delegation_set.go
   [7/100] internal/service/route53/delegation_set_data_source.go
   [8/100] internal/service/route53/equal.go
   [9/100] internal/service/route53/errors.go
   [100/100] internal/service/route53resolver/validate.go
   Common functions: 43
✅ Wrote route53-read.json (19 actions)
✅ Wrote route53-write.json (24 actions)
[ec2-user@ip-172-31-35-35 ~]$ cat route53-write.json 
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "route53:ActivateKeySigningKey",
                "route53:AssociateVPCWithHostedZone",
                "route53:ChangeCidrCollection",
                "route53:ChangeResourceRecordSets",
                "route53:ChangeTagsForResource",
                "route53:CreateCidrCollection",
                "route53:CreateHealthCheck",
                "route53:CreateHostedZone",
                "route53:CreateKeySigningKey",
                "route53:CreateQueryLoggingConfig",
                "route53:CreateReusableDelegationSet",
                "route53:CreateTrafficPolicy",
                "route53:CreateTrafficPolicyInstance",
                "route53:CreateVPCAssociationAuthorization",
                "route53:DeactivateKeySigningKey",
                "route53:DeleteHostedZone",
                "route53:DisableHostedZoneDNSSEC",
                "route53:DisassociateVPCFromHostedZone",
                "route53:EnableHostedZoneDNSSEC",
                "route53:UpdateHealthCheck",
                "route53:UpdateHostedZoneComment",
                "route53:UpdateHostedZoneFeatures",
                "route53:UpdateTrafficPolicyComment",
                "route53:UpdateTrafficPolicyInstance"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "eu-central-1",
                    "aws:RequestTag/Env": [
                        "Dev"
                    ]
                }
            }
        }
    ]
}
```




