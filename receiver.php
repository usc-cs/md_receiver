<?php
include('secret.php');

$headers = getallheaders();
$hubSignature = $headers['X-Hub-Signature'];
list($algo, $hash) = explode('=', $hubSignature, 2);

$payload = $HTTP_RAW_POST_DATA;
$data = json_decode($payload);
$payloadHash = hash_hmac($algo, $payload, $secret);

// if it's not sent from github, kill it.
if ($hash !== $payloadHash) {
  die('Unauthorized');
}

if ($data->ref == 'refs/heads/deploy') {
        echo shell_exec('python receiver.py ' . $data->repository->full_name);
        echo 'success ' . $data->repository->full_name;
} else {
        echo 'not deploy branch';
}
?>

success
