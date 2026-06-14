package org.example.recommendation_system.repo;

import org.example.recommendation_system.model.User;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepo extends Neo4jRepository<User, String> {
    User findByUsername (String username);
}
