import type { Route } from "./+types/home";
import { HomeContent } from "~/components/home-content";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "OLLEH - See it. Love it. Own it." },
    { name: "description", content: "Confidence should not wait for payday. Secure the fashion you love today." },
  ];
}

export default function Home() {
  return <HomeContent />;
}
