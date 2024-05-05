import os
import json
import re
import boto
import boto.s3.connection

from django.conf import settings

from src.celery import app


# NOTE Celery doesn't allow methods as tasks. So we handle this
# by defining some proxy functions

# pylint: disable-msg=unused-argument
@app.task(bind=True, name="bucket.pull_file_task")
def pull_file_task(self, path, overwrite):
    bucket = Bucket()
    return bucket.pull_file(path, overwrite)


@app.task(bind=True, name="bucket.push_file_task")
def push_file_task(self, path, overwrite):
    bucket = Bucket()
    return bucket.push_file(path, overwrite)


class Bucket:
    def __init__(
        self,
        name=settings.CDN_BUCKET_NAME,
        local_dir=settings.PROJECT_ROOT + "/buckets/<bucket_name>/",
    ):
        # TODO keep conn var or not?
        conn = boto.connect_s3(
            aws_access_key_id=settings.CDN_ACCESS_KEY,
            aws_secret_access_key=settings.CDN_SECRET_KEY,
            host=settings.CDN_ENDPOINT,
            is_secure=False,  # TODO SSL
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )

        # TODO # OPTIMIZE : Can put argument validate=False
        self.bucket = conn.get_bucket(name)
        self.local_dir = local_dir.replace("<bucket_name>", name)
        os.makedirs(self.local_dir, exist_ok=True)

    def push_file(self, path, overwrite=False):
        """
            Pushes a file "path" relative to local_dir to the bucket
        """
        if not overwrite and self.file_exists(path):
            raise RuntimeError(
                "File already exists in bucket and overwrite argument is False: " + path
            )

        key = self.bucket.new_key(path)
        key.set_contents_from_filename(self.local_dir + path)
        key = self.bucket.get_key(path)
        key.set_canned_acl("public-read")

    def pull_file(self, path, overwrite=False):
        if not overwrite and os.path.exists(self.local_dir + path):
            raise RuntimeError(
                "File already exists locally and overwrite argument is False: " + path
            )
        key = self.bucket.new_key(path)
        key.get_contents_to_filename(self.local_dir + path)

    def update_version(self):
        # version = re.sub(
        #     "[: -]", "", str(datetime.now(timezone.utc))[:19]
        # )
        ignore_files = [
            "version.json",
            "keylist.json",
        ]
        ignore_regexs = [r"^img\/.*", r"^analysis_files/.*"]
        ignore_regexs = "|".join(ignore_regexs)
        data = [
            {"filename": key.name, "last_modified": key.last_modified}
            for key in self.bucket.list()
            if key.name not in ignore_files and not re.match(ignore_regexs, key.name)
        ]
        path = "keylist.json"
        with open(self.local_dir + path, "w") as f:
            json.dump(data, f)

        key = self.bucket.new_key(path)
        key.set_contents_from_filename(self.local_dir + path)
        self.bucket.get_key(path).set_canned_acl("public-read")

        data = map(lambda x: x["last_modified"], data)
        version = max(data)
        data = {"version": version}
        path = "version.json"
        with open(self.local_dir + path, "w") as f:
            json.dump(data, f)

        key = self.bucket.new_key(path)
        key.set_contents_from_filename(self.local_dir + path)
        self.bucket.get_key(path).set_canned_acl("public-read")

    def file_exists(self, path):
        return path in [key.name for key in self.bucket.list()]

    def search_file(self, pattern):
        return [key.name for key in self.bucket.list() if re.match(pattern, key.name)]
