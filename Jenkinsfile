#!/usr/bin/env groovy

@Library("jenkinstools@master") _
import com.splunk.jenkins.DockerRequest;

withSplunkWrapNode("master") {
    stage('checking'){
        steps {
                sh 'echo "Hello World"'
                
            }
    }
}   
