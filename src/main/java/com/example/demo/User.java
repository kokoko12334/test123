package com.example.demo;

public class User {
	private final String name;
	private final int age;
	private final String email;
	private final String phone;

	// private 생성자: Builder를 통해서만 생성 가능
	private User(Builder builder) {
		this.name = builder.name;
		this.age = builder.age;
		this.email = builder.email;
		this.phone = builder.phone;
	}

	// 정적 Builder 클래스
	public static class Builder {
		private String name;
		private int age;
		private String email;
		private String phone;

		public Builder name(String name) {
			this.name = name;
			return this;
		}

		public Builder age(int age) {
			this.age = age;
			return this;
		}

		public Builder email(String email) {
			this.email = email;
			return this;
		}

		public Builder phone(String phone) {
			this.phone = phone;
			return this;
		}

		public User build() {
			return new User(this);
		}
	}

	// Getter 메서드
	public String getName() {
		return name;
	}

	public int getAge() {
		return age;
	}

	public String getEmail() {
		return email;
	}

	public String getPhone() {
		return phone;
	}
}

