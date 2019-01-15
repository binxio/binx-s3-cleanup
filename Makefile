.PHONY: help launch deploy redeploy remake-buckets upload-content cleanup-test-content cleanup-deployment-content deployment-bucket build package delete
.DEFAULT_GOAL := run

## set your profile name as ENVIRONMENT
ENVIRONMENT = "binx"
BUCKET_NAME="binx-cleanup-lambda"

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

launch: deployment-bucket deploy upload-content

deploy: build package
	@sceptre launch $(ENVIRONMENT)

redeploy: cleanup-test-content remake-buckets upload-content

remake-buckets:
	@sceptre delete $(ENVIRONMENT)/eu/ocp-buckets.yaml
	@sceptre launch $(ENVIRONMENT)/eu/ocp-buckets.yaml

upload-content:
	## copy some test content to the buckets
	aws s3 cp bucket-content/index1.html s3://$(ENVIRONMENT)-s3-cleanup-bucket1/index1.html
	aws s3 cp bucket-content/index2.html s3://$(ENVIRONMENT)-s3-cleanup-bucket2/index2.html
	aws s3 cp bucket-content/hello.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket3/hello.txt
	aws s3 cp bucket-content/real-content.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket4/real-content.txt
	aws s3 cp bucket-content/hello.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket5/hello.txt
	aws s3 cp bucket-content/real-content.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket5/real-content.txt

cleanup-test-content:
	-aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket1 --recursive
	-aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket2 --recursive
	-aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket3 --recursive
	-aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket4 --recursive
	-aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket5 --recursive

cleanup-deployment-content:
	aws s3 rm s3://binx-cleanup-lambda --recursive

deployment-bucket:
	@sceptre launch $(ENVIRONMENT)/eu/bucket.yaml

build:
	sam build \
		-s lambdas/ \
		-t sam-templates/s3cleanup.yaml \
		-m lambdas/requirements.txt \
		--use-container

package:
	sam package \
		--output-template-file templates/s3cleanup.yaml \
		--s3-bucket $(BUCKET_NAME)

delete: cleanup-test-content cleanup-deployment-content
	@sceptre delete $(ENVIRONMENT)