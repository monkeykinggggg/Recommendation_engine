package org.example.recommendation_system.controller;

import org.example.recommendation_system.model.User;
import org.example.recommendation_system.service.JWTService;
import org.example.recommendation_system.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;


@RestController
public class UserController {


    @Autowired
    private UserService service;

    @Autowired
    private AuthenticationManager authenticationManager;  // this way we can use the object created as bean in Security Configuration


    @Autowired
    private JWTService jwtService;

    // in first security app this endpoint was also secure bc all the endpoints were secure, now we change it: in SecurityConfig
    @PostMapping("/register")
    public User register(@RequestBody User user){

        return service.saveUser(user);
    }

    @PostMapping("/login")
    public String login(@RequestBody User user){
        Authentication authentication = authenticationManager
                .authenticate(new UsernamePasswordAuthenticationToken(user.getUsername(), user.getPassword()));
        if(authentication.isAuthenticated()){
            //return "Success. Authenticated";
            return jwtService.generateToken(user.getUsername());
        }
        else{
            return "Login Failed";
        }
    }

}
