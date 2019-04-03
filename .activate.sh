# The simple scripting for development
export PROJECT_NAME="Django Chat App"
export PROJECT_PREFIX="chatapp"
export ENVIRONMENT="dev"
export ENVIRONMENT_LIST=(
    "dev"
    "prod"
    "test"
)

function print_header {
    echo "
Project name: ${PROJECT_NAME}
Prefix: ${PROJECT_PREFIX}
Environment: ${ENVIRONMENT}
"
}


function chatapp-login {
    ENVIRONMENT=$1
    print_header
}

function chatapp-compose {
    command=$@
    ENVIRONMENT=$ENVIRONMENT docker-compose -f "docker-compose.${ENVIRONMENT}.yml" ${command}
}

function chatapp-build {
    ENVIRONMENT=$1
    print_header
    chatapp-compose build
}

function chatapp-run {
    ENVIRONMENT=$1
    print_header
    chatapp-compose up
}


for env in ${ENVIRONMENT_LIST[@]}; do
    alias "${PROJECT_PREFIX}-login-${env}"="${PROJECT_PREFIX}-login ${env}"
    alias "chatapp-${env}-build"="chatapp-build ${env}"
    alias "chatapp-${env}-run"="chatapp-run ${env}"
done

print_header
