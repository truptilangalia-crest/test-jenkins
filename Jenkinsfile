#!/usr/bin/env groovy

@Library("jenkinstools@master") _

import com.splunk.jenkins.Utilities
import com.splunk.jenkins.DockerRequest;
import com.splunk.tool.plugin.docker.extension.BadDockerExitCode;

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
    def artifactory_branch = repoBranch
    def splunkTestAgainst = ["logan"]
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


    // recording Jobs keys for creating jenkins reports
    def e2eJobList = ""

    // Process builds

    def splunkCommitNum = ""
    def splunkURL = ""

    def dockerReq = ""
    def repoName = ""

    // Process builds
    def tas = ""
    def ta_builds = ""
    def escu_build = ""
    def mustang_da_build = ""
    def local_app_installer = ""
    def type = "S1"

    if (tas.isEmpty())
        tas = "TA-Kinesis_a"
    echo("tas: ${tas}")
    if(ta_builds.isEmpty())
    {
        def ta_kinesis_fn = sh(returnStdout: true, script: 'wget -q 2>&1 -O - https://repo.splunk.com/artifactory/Solutions/TA/ta-aws-kinesis-firehose/kinesis-mustang-builds/all-builds/latest/ | awk \"/.spl|tar.gz/{print $2}\"')
        ta_kinesis_fn = ta_kinesis_fn.substring(ta_kinesis_fn.indexOf('>') + 1, ta_kinesis_fn.indexOf('</a>'))
        def o365_fn = sh(returnStdout: true, script: 'wget -q 2>&1 -O - https://repo.splunk.com/artifactory/Solutions/TA/ta-office365/o365-mustang-builds/releases/Mustang-GA/ | awk \"/spl|tar.gz/{print $2}\"')
        o365_fn = o365_fn.substring(o365_fn.indexOf('>') + 1, o365_fn.indexOf('</a>'))
        ta_builds = "https://repo.splunk.com/artifactory/Solutions/TA/ta-aws-kinesis-firehose/kinesis-mustang-builds/all-builds/latest/" + ta_kinesis_fn + "," + "https://repo.splunk.com/artifactory/Solutions/TA/ta-office365/o365-mustang-builds/releases/Mustang-GA/" + o365_fn
    }
    echo("ta_builds: ${ta_builds}")
    def ta_s = ta_builds.split(',')
    for( String values : ta_s )
        local_app_installer = local_app_installer + values + " "
    if(escu_build.isEmpty())
    {
        def escu = "https://repo.splunk.com/artifactory/Solutions/DA/da-ess-amazonwebservices-content/latest/"
        def escu_fn = sh(returnStdout: true, script: 'wget -q 2>&1 -O - https://repo.splunk.com/artifactory/Solutions/DA/da-ess-amazonwebservices-content/latest/ | awk \"/spl|tar.gz/{print $2}\"')
        escu_fn = escu_fn.substring(escu_fn.indexOf('>') + 1, escu_fn.indexOf('</a>'))
        escu_build = "https://repo.splunk.com/artifactory/Solutions/DA/da-ess-amazonwebservices-content/latest/" + escu_fn
    }
    echo("escu_build: ${escu_build}")
    local_app_installer = local_app_installer + escu_build + " "
    if(mustang_da_build.isEmpty())
    {
        def mustang_da = "https://repo.splunk.com/artifactory/Solutions/DA/da-ess-aws/releases/1.0.x/1.0.0/"
        def mustang_da_fn = sh(returnStdout: true, script: 'wget -q 2>&1 -O - https://repo.splunk.com/artifactory/Solutions/DA/da-ess-aws/releases/1.0.x/1.0.0/ | awk "/spl|tar.gz/{print $2}"')
        mustang_da_fn = mustang_da_fn.substring(mustang_da_fn.indexOf('>') + 1, mustang_da_fn.indexOf('</a>'))
        mustang_da_build = "https://repo.splunk.com/artifactory/Solutions/DA/da-ess-aws/releases/1.0.x/1.0.0/" + mustang_da_fn
    }
    echo("mustang_da_build: ${mustang_da_build}")
    local_app_installer = local_app_installer + mustang_da_build
    def apps = "app-ess"
    def app_versions = "${artifactory_branch}"
    echo("local_app_installer ${local_app_installer}")
    if (!escu_build?.trim())
    {
        apps = apps + " da-ess-contentupdate"
        app_versions = app_versions + " latest"
    }
    if (!mustang_da_build?.trim())
    {
        apps = apps + " da-ess-aws"
        app_versions = app_versions + " latest"
    }
    if (!ta_builds?.trim())
    {
        for( String values : ta_s )
        {
            apps = apps + " values"
            app_versions = app_versions + " latest"
        }
    }

    stage('Checkout') {
        withCredentials([usernamePassword(credentialsId: 'jenkins_qa_auto_user', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]){
            repoName = "https://$USERNAME:$PASSWORD@git.splunk.com/scm/soln/app-ess.git"
            dockerReq = new DockerRequest(steps, currentBuild, env, [
                imageName: buildImage,
                userId: "10777",
                repoName: repoName,
                branchName: repoBranch,
                runner: "yarn" ]);
            splunkPrepareAndCheckOut cloneImageName: buildImage, repoName: repoName, branchName: repoBranch;
        }
    }

    if(generateManifest){
        stage('Manifest Generation'){
            splunkRunScript request: dockerReq,
                script: """
                    cd /build/app-ess
                    cd test/e2e/correlation_searches/datf
                    python3 -m pip install -r requirements.txt
                    cd ../escu-automation/cim_report_parser
                    python3 temp_manifest_init.py
                    chmod -R 777 .
                    cat temp_manifest_init.py
                    cp temp_manifest_init.json /build
                """;
            // sh('echo "Hello')
            sh('ls -la')
            sh('mkdir build')
            splunkDockerCopyFile files: "/build/*.json" , remotePath: "/build";
            sh('cd build && ls -la')
            sh('ls -la')
        }
    }
    try {
        def jobs = [:]

        // // Only run on schedule against develop branch OR run if triggered by a user
        // withCredentials([usernamePassword(credentialsId: 'jenkins_qa_auto_user', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {

        //     for (s in splunkTestAgainst) {

        //          def splunkBranch = s


        //             def tas_s = tas.split(',')
        //             for( String ta : tas_s ) {
        //                 def jobNameE2ECorrelation = "ES-DATF-E2E-Correlation--S1-${splunkBranch}_${ta}"
        //                 def ta_param = ta

        //                 def appKoalaArgsE2ECorrelation = """
        //                     --apps ${apps}
        //                     --app_versions ${app_versions}
        //                     --with_sample false
        //                     --splunk_pass ${splunk_pass}
        //                     --local_app_installer ${local_app_installer}
        //                 """.stripIndent().replaceAll("\n", " ")

        //                 def testcubeMarkerE2ECorrelation = """
        //                     --feature=e2e.correlation_searches.datf
        //                     --infra-type=ucp --deployment-type=${type}
        //                     --skip-pytest-dry-run
        //                     --skip-flaky-test
        //                     --collect-log-mode=fail --collect-log-count=2
        //                     --appkoala-args="${appKoalaArgsE2ECorrelation}"
        //                 """.stripIndent().replaceAll("\n", " ")

        //                 echo("testcubeMarkerE2ECorrelation ${testcubeMarkerE2ECorrelation}")

        //                 jobs[jobNameE2ECorrelation] = {
        //                     splunkDockerCopyFile files: "/build/*.json" , remotePath: "/build", allowMissingFiles:false;
        //                     splunkFunctionalTest repoName : "https://$USERNAME:$PASSWORD@git.splunk.com/scm/soln/app-ess.git",
        //                         runner: "orca",
        //                         orcaCredentialId: orcaCredentialId,
        //                         orcaVersion: orcaVersion,
        //                         orcaAnsibleLog: "/dev/stdout",
        //                         args: "--preserve --tsc datf_e2e_CorrelationSearch --runner-args '--junit-prefix ${jobNameE2ECorrelation} --testadmin ${splunkAdminUsername} --testanalyst ${splunkAnalystUsername} --testuser ${splunkUserUsername} --testpass ${splunkPassword} --tas ${ta_param}' --splunk-branch '${splunkBranch}' --testcube-marker '${testcubeMarkerE2ECorrelation}' ${orcaResource}",
        //                         appStatus: "builds",
        //                         branchName: repoBranch,
        //                         artifactoryBranch: repoBranch,
        //                         reportPrefix: jobNameE2ECorrelation,
        //                         orcaVerbose: orcaVerbose,
        //                         debugMode: "sleep",
        //                         withSample: false,
        //                         aggregateFiles: "/build/.orca/logs/,${solnRoot}/app-ess/test-results/",
        //                         enableOrcaS3Archive: true,
        //                         s3BucketName: s3BucketName,
        //                         s3BucketCredentialId: s3BucketCredentialId,
        //                         s3UseGzip: s3UseGzip
        //                 }
        //          }
        //     }

        //     e2eJobList = jobs.keySet()
        //     timeout(time: 4, unit: 'HOURS') {
        //         stage("Test - Functional E2E") {
        //             parallel jobs
        //         }
        //     }
        // }
        
        
        println "Hello, This is test execution stage"
    } catch (Exception e) {
            echo "Exception Caught: ${e.getMessage()}"
            currentBuild.result = 'FAILURE';
    } finally {
        stage('Archive Results') {
            println "archive results stage"
            splunkCopyFromDocker remotePath: "/build/", allowMissingFiles: true, files: "*.json";
            archiveArtifacts artifacts : "target/**/*", allowEmptyArchive: true
        }
        stage('Clean') {
            println "Clean Jenkins workspace"
            cleanWs()
        }
    }
}
