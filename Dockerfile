FROM openjdk:17
EXPOSE 8085
ADD target/test2.jar test2.jar
ENTRYPOINT ["java","-jar","/test2"]
CMD ["/bin/sh"]
