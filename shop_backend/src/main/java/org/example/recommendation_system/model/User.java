package org.example.recommendation_system.model;

import lombok.Data;
import org.springframework.data.neo4j.core.schema.*;
import org.springframework.data.neo4j.core.support.UUIDStringGenerator;

@Node("User")
@Data   // for setters getters
public class User {
    @Id @GeneratedValue(UUIDStringGenerator.class)
    @Property("user_id")
    private String userId;

    @Property("username")
    private String username;

    @Property("password")
    private String password;
}
