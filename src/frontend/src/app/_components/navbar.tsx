"use client";

import * as React from "react";
import Link from "next/link";
import Image from "next/image";

import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/app/_components/ui/navigation-menu";
import { Button } from "./ui/button";

export function Navbar() {
  return (
    <NavigationMenu className="w-full top-6 sticky h-fit m-6 gap-12">
      <NavigationMenuList className="gap-5">
        <NavigationMenuItem>
          <Link href="/" legacyBehavior passHref>
            <NavigationMenuLink
              className={`${navigationMenuTriggerStyle()} bg-black`}
              asChild
            >
              <Button variant={"ghost"} className="bg-transparent">
                <Image
                  src={"/ambalabu-text.png"}
                  alt={"ambalabu"}
                  width={100}
                  height={100}
                  className="h-9 w-fit"
                />
              </Button>
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}
