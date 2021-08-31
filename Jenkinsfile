#!/usr/bin/env groovy

@Library("jenkinstools@master") _
import com.splunk.jenkins.DockerRequest;

withSplunkWrapNode("master") {

    def spl_versions = "8.2.2"
    
    properties([
        parameters([
            string(name: 'repoBranch', defaultValue: "test/temp_ESCU_automation", description: 'app-ess repo branch to be run test', trim: true),
            string(name: 'paramSplunkVersion', defaultValue: spl_versions, description: 'Comma separated list of splunk versions, names or commits, eg. - 7.2.10,7.3.5,8.0.2,8.1.0,8.0.2001,8.0.2003.', trim: true),
            choice(
                        name: 'splunk_deployment_type',
                        choices: 'S1 (Single instance standalone)\nC1 (Distributed 3 indexers 1 search head, clustered)\nC3 (Distributed 3 indexers, 3 search heads, clustered)',
                        description: 'Select a Splunk type from S1(Single instance standalone), C1(Distributed 3 indexers 1 search head, clustered), C3(Distributed 3 indexers, 3 search heads, clustered)'),
            choice(
                        name: 'splunk_infra_type',
                        choices: 'ucp\naws_ec2',
                        description: 'Select a Splunk type from ucp, aws_ec2'),
            booleanParam(name: 'generate_manifest', defaultValue: true, description: 'Generate manifest file'),
            string(name: 'detections', defaultValue: 'cloud,endpoint,network', description: 'Select detection type to be tested', trim: true),
            string(name: 'additional_filter', defaultValue: '', description: 'additional filtering of detection tests, e.g. abnormally_high_number_of_cloud_infrastructure_api_calls', trim: true),
        ])
    ])

    def buildImage = "repo.splunk.com/splunk/app-automation/app-build:20.3.15"

    // Get the Jenkins pipeline values in variables
    def repoBranch = params.repoBranch
    def splunkTestAgainst = params.paramSplunkVersion
    def splunkDeploymentType = params.splunk_deployment_type
    def splunkInfraType = params.splunk_infra_type
    def generateManifest = params.generate_manifest
    def detectionType = params.detections
    def additionalFilter = params.additional_filter


    // Set orca 
    def orcaVersion = "1.2.0.2"
    def orcaCredentialId = "srv-ucp-es-only"
    def orcaResource = " --reserve-cpu 1 --reserve-memory 2 --limit-cpu 14 --limit-memory 12 "
    def orcaVerbose = true

    def ansibleLog = "/build/app-ess/ansible.log"
    def s3BucketName = 'bucket-jenkins-builds-data-bucket-ni9gsg2txxxn' // the S3 bucket that test artifacts are uploaded to
    def s3BucketCredentialId = 'infra_aws_s3'                           // credential to upload to the S3 bucket
    def s3UseGzip = true
    def solnRoot = "/build"
    def appStatus = "builds"

    // Splunk details
    def splunkAdminUsername = "admin"
    def splunkAnalystUsername = "esanalyst"
    def splunkUserUsername = "esuser"
    def splunkPassword = "changeme"
    def splunk_pass = "Chang3d!"

    def apps = "app-ess"

    // recording Jobs keys for creating jenkins reports
    def e2eJobList = ""

    // Process builds

    def local_app_installer = ""
    def splunkCommitNum = ""
    def splunkURL = ""

    def dockerReq = ""
    def repoName = ""
    
    stage('checking'){
        steps {
                sh 'echo "Hello World"'
                
            }
    }
}   
