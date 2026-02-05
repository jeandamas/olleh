import { type RouteConfig, index,route } from "@react-router/dev/routes";


export default [index("routes/home.tsx"), 
                route("/login", "routes/auth/login.tsx"),
                route("/signup", "routes/auth/signup.tsx"),
                route("/dashboard", "routes/client/dashboard.tsx"),
                route("/packages/pricing", "routes/packages/pricing.tsx"),
                route("/memberships/request/:id", "routes/memberships/request.$id.tsx"),
            ] satisfies RouteConfig;
