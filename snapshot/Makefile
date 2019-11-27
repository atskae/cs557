.PHONY: python clean

python: branch controller

clean:
	rm -f controller branch
	rm -f *.pyc

protoc_middleman: bank.proto
	protoc $$PROTO_PATH --python_out=. bank.proto
	@touch protoc_middleman

controller: src/run-controller.py protoc_middleman
	@echo "Creating controller script"
	@echo '#! /bin/sh' > controller
	@echo './src/run-controller.py "$$@"' >> controller
	@chmod +x controller

branch: src/run-branch.py protoc_middleman
	@echo "Creating branch script"
	@echo '#! /bin/sh' > branch
	@echo './src/run-branch.py "$$@"' >> branch
	@chmod +x branch
