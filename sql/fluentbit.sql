
CREATE TABLE IF NOT EXISTS public.fluentbit
(
    tag character varying COLLATE pg_catalog."default",
    "time" timestamp without time zone,
    data jsonb
);
\i grant.sql

/*
tag:
kube.var.log.containers.ekkapp-1_ns-eis-prelive_ekkapp-d361974cfd947862144a9cb138bb7f6c43119f7193c943987b786f2ab86e300b.log
data:
 {
  "log": "2024-03-08T09:21:09.801175939+02:00 stderr F 09:21:09,800 ERROR 139757733615296 [eis.lib.errorhandler]  S3Error('S3 operation failed; code: NoSuchKey, message: The specified key does not exist., resource: /eis/avalehepilt/000/000/001.36T15rPZ, request_id: 17BAB90C03867CB4, host_id: 6008fa4fca9724794957431f1b601abef4f4d0a7ea602326c858484a7fb219ca, bucket_name: eis, object_name: avalehepilt/000/000/001.36T15rPZ')\n",
  "date": 1709882469.801584
}
*/
