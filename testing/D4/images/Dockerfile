# SPDX-License-Identifier: GPL-3.0-only
ARG JAVA_IMAGE
FROM ${JAVA_IMAGE}
ARG LAB_UID=1000
ARG LAB_GID=1000
COPY classes /app/classes
COPY lib /app/lib
COPY sql /sql
USER ${LAB_UID}:${LAB_GID}
WORKDIR /app
ENTRYPOINT ["java","-XX:MaxRAMPercentage=65","-cp","/app/classes:/app/lib/*","io.github.isidorotrevino.planner.lab.LabMain"]
