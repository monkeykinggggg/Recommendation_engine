package org.example.recommendation_system.service;


import org.example.recommendation_system.model.User;
import org.example.recommendation_system.repo.UserRepo;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    @Autowired
    private UserRepo repo;
    private BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public User saveUser(User user){
        user.setPassword(encoder.encode(user.getPassword()));   // encoding the password before assigning in database
        System.out.println(user.getPassword());
        return repo.save(user);
    }
}
