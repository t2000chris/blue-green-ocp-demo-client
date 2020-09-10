FROM registry.access.redhat.com/ubi8/ubi
EXPOSE 8080
CMD python -m http.server 8080
