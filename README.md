# Clever Llamas Llamaverse Gradle Plugin
<!-- [![Build Status](https://travis-ci.org/cleverllama/llamaverse.svg?branch=master)](https://travis-ci.org/cleverllama/llamaverse)
[![Maven Central](https://img.shields.io/maven-central/v/com.cleverllama/llamaverse.svg)](https://search.maven.org/artifact/com.cleverllama/llamaverse) -->
Gradle Plugin for the Clever Llamas Llamaverse



To Publish locally, you can use the following command:

./gradlew publishToMavenLocal

This will publish to your local machine's maven repo.  For \*NIX machines, it is located under [user-home]/.m2/repository

``` 
.m2
└── repository
    └── com
        ├── cleverllamas
        │   └── llamaverse
        │       ├── 1.0.0
        │       │   ├── llamaverse-1.0.0.jar
        │       │   └── llamaverse-1.0.0.pom
        │       └── maven-metadata-local.xml

```


Please note that locally, still Maven will cache internally.  You may also want to up the number.  If you want to continue to republisg the same number, that is possible by clearing the gradle cache, but that can have an effect on other orojects.  This will be

// build.gradle
version = "1.0.0"

