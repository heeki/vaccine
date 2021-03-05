let simple = process.env.SIMPLE_RESPONSE;
let allow_token = process.env.ALLOW_TOKEN;

exports.handler =  function(event, context, callback) {
    console.log(JSON.stringify(event));
    var token = '';
    var resource = '';
    var context = {};
    // v1
    if ('methodArn' in event) {
        resource = event.methodArn;
        context.pversion = '1.0';
        context.simple = 'false';
    // v2
    } else if (event.version == '2.0' && 'routeArn' in event) {
        // resource = event.routeArn + '/*';
        resource = event.routeArn;
        context.pversion = event.version;
        context.simple = simple;
    }
    if ('authorization' in event.headers) {
        token = event.headers.authorization;
    } else if ('Authorization' in event.headers) {
        token = event.headers.Authorization;
    }
    context.token = token;
    switch (token) {
        case allow_token:
            context.reason = 'generating allow policy'
            callback(null, generatePolicy('user', 'Allow', resource, context));
            break;
        case 'deny':
            context.reason = 'generating deny policy';
            callback(null, generatePolicy('user', 'Deny', resource, context));
            break;
        default:
            context.reason = 'invalid token provided';
            callback(null, generatePolicy('user', 'Deny', resource, context));
    }
};

var generatePolicy = function(principalId, effect, resource, context) {
    var authResponse = {};
    if (simple == "true") {
        switch (effect) {
            case 'Allow':
                authResponse.isAuthorized = true;
                break;
            case 'Deny':
                authResponse.isAuthorized = false;
                break;
            default:
                authResponse.isAuthorized = false;
                break;
        }
    } else {
        authResponse.principalId = principalId;
        if (effect && resource) {
            var policyDocument = {};
            policyDocument.Version = '2012-10-17';
            policyDocument.Statement = [];
            var statementOne = {};
            statementOne.Action = 'execute-api:Invoke';
            statementOne.Effect = effect;
            statementOne.Resource = resource;
            policyDocument.Statement[0] = statementOne;
            authResponse.policyDocument = policyDocument;
        }
    }
    authResponse.context = context;
    console.log(JSON.stringify(authResponse));
    return authResponse;
}