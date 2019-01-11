.PHONY: help deploy upload-content cleanup-content delete deployment-bucket build package
.DEFAULT_GOAL := run

## set your profile name as ENVIRONMENT
ENVIRONMENT = "binx"
BUCKET_NAME="binx-cleanup-lambda"

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

deploy: build package
	@sceptre launch $(ENVIRONMENT)

upload-content:
	## copy some test content to the buckets
	aws s3 cp bucket-content/index1.html s3://$(ENVIRONMENT)-s3-cleanup-bucket1/index1.html
	aws s3 cp bucket-content/index2.html s3://$(ENVIRONMENT)-s3-cleanup-bucket2/index2.html
	aws s3 cp bucket-content/hello.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket3/hello.txt
	aws s3 cp bucket-content/real-content.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket4/real-content.txt
	aws s3 cp bucket-content/hello.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket5/hello.txt
	aws s3 cp bucket-content/real-content.txt s3://$(ENVIRONMENT)-s3-cleanup-bucket5/real-content.txt

cleanup-content:
	## clean the test content in the buckets
	aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket1 --recursive
	aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket2 --recursive
	aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket3 --recursive
	aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket4 --recursive
	aws s3 rm s3://$(ENVIRONMENT)-s3-cleanup-bucket5 --recursive

	#cleanup deployment bucket
	aws s3 rm s3://binx-cleanup-lambda --recursive

delete:
	@sceptre delete $(ENVIRONMENT)

deployment-bucket:
	@sceptre launch $(ENVIRONMENT)/eu/bucket.yaml

build:
	export AWS_PROFILE=$(ENVIRONMENT)
	sam build \
		-s lambdas/ \
		-t sam-templates/s3cleanup.yaml \
		-m lambdas/requirements.txt \
		--use-container

package:
	export AWS_PROFILE=$(ENVIRONMENT)
	sam package \
		--output-template-file templates/s3cleanup.yaml \
		--s3-bucket $(BUCKET_NAME)