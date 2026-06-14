package org.example.recommendation_system.repo;

import org.example.recommendation_system.model.Product;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProductRepo extends Neo4jRepository<Product, String> {
    Product findByParentAsin(String parentAsin);

    @Query("MATCH (p:Product) RETURN p ORDER BY rand() LIMIT $limit")
    List<Product> findSeveralRandomProducts(int limit);
}
