
PROJECT_NAME=dbrows

DB_NAME=dbname
DB_PASS=dbpass
DB_USER=dbuser


MYSQL_VERSIONS    = 5.6 5.7 8 latest
POSTGRES_VERSIONS = 9.5 # 9.6 10 11 12 13 latest


ENV=\
	DB_NAME=$(DB_NAME) \
	DB_PASS=$(DB_PASS) \
	DB_USER=$(DB_USER) \
	PYTHON_VERSION=$(PYTHON_VERSION) \
	DB_ENGINE=$(DB_ENGINE) \
	DB_VERSION=$(DB_VERSION)

MAKE_BUILD_CMD=docker-compose -f docker-compose-$(DB_ENGINE).yml build --parallel db test
MAKE_TEST_RUN=docker-compose -f docker-compose-$(DB_ENGINE).yml run test pytest .

test-run:
	$(MAKE_TEST_RUN)

test-build:
	$(MAKE_BUILD_CMD)

test-build-postgres:
	$(eval DB_ENGINE=postgres)
	$(ENV) $(MAKE_BUILD_CMD)

test-run-postgres: test-build-postgres
	$(eval DB_ENGINE=postgres)
	$(ENV) $(MAKE_TEST_RUN)

test-build-mysql:
	$(eval DB_ENGINE=mysql)
	$(ENV) $(MAKE_BUILD_CMD)

test-run-mysql: test-build-mysql
	$(eval DB_ENGINE=mysql)
	$(ENV) $(MAKE_TEST_RUN)


test-run-postgres-all:
	for version in $(POSTGRES_VERSIONS); do \
  		echo $$version; \
  		$(eval DB_VERSION=$(version) ) \
  		echo ${$DB_VERSION}; \
		$(eval DB_ENGINE=postgres) \
		$(eval DB_VERSION=$$version ) \
		$(ENV) $(MAKE_TEST_RUN); \
	done


help:
	@echo ""
	@echo "make test DB_TYPE=postgres"


.DEFAULT_GOAL := help
.PHONY: help
